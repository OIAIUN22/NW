# Module BSP 通用 C++17 接口

这一层不是“SG90 接口”，而是**面向 BSP 的通用 C++17 适配层**：

```text
app
 │ 只依赖 module::bsp::IUart / II2c / ICan
 ▼
module/bsp/i_bus.hpp
 ▲
 │ 实现
module/bsp/adapters.cpp  ── extern "C" ──►  bsp/uart、bsp/i2c、bsp/can（C 编译）
```

目标：

- 把 C BSP 的 `bsp_xxx_status_t` 映射成统一的 `module::bsp::Status`；
- 把 C 函数指针/长度参数封装成 `ByteView`、`CanFrame`；
- 让 app/module 不直接 include BSP 头、不直接调用 C 函数；
- C++17：`enum class`、`[[nodiscard]]`、`std::string_view`、`final/override`；
- 不使用异常、RTTI、动态内存。

## 目录

```text
module/
├─ bsp/
│  ├─ types.hpp       # Status、ByteView、CanFrame、IBspDevice
│  ├─ i_bus.hpp       # IUart、II2c、ICan
│  ├─ adapters.hpp    # C BSP 适配器声明
│  ├─ adapters.cpp    # extern "C" 调 C BSP，映射状态
│  └─ README.md
├─ servo/             # SG90 设备模块（示例）
└─ interfaces/        # 设备级接口（如 IServo）
```

## 公共契约

`module/bsp/types.hpp`：

```cpp
enum class Status : std::uint8_t {
    Ok = 0,
    InvalidArgument,
    NotReady,
    Busy,
    Timeout,
    BusError,
    InitFailed,
    NotSupported,
};

struct ByteView {
    const std::uint8_t* data{nullptr};
    std::size_t size{0};
    // ...
};

struct CanFrame {
    std::uint32_t id{0};
    std::uint8_t len{0};
    std::array<std::uint8_t, 8> data{};
    bool extended{false};
    bool remote{false};
};

class IBspDevice {
public:
    virtual ~IBspDevice() = default;
    [[nodiscard]] virtual Status init() = 0;
    [[nodiscard]] virtual bool ready() const noexcept = 0;
    [[nodiscard]] virtual std::string_view name() const noexcept = 0;
};
```

为什么用 `ByteView` 而不是 `std::span`：

- `std::span` 是 C++20；
- 本项目是 C++17；
- `ByteView` 只是一个“指针 + 长度”，不拥有内存，调用期间有效即可。

## 三个能力接口

`module/bsp/i_bus.hpp`：

```cpp
class IUart : public IBspDevice {
public:
    [[nodiscard]] virtual Status write(ByteView data,
                                       std::uint32_t timeout_ms) = 0;
};

class II2c : public IBspDevice {
public:
    [[nodiscard]] virtual Status write(std::uint8_t addr7,
                                       ByteView data,
                                       std::uint32_t timeout_ms) = 0;
    [[nodiscard]] virtual Status writeReg(std::uint8_t addr7,
                                          std::uint8_t reg,
                                          ByteView data,
                                          std::uint32_t timeout_ms) = 0;
};

class ICan : public IBspDevice {
public:
    [[nodiscard]] virtual Status send(const CanFrame& frame,
                                      std::uint32_t timeout_ms) = 0;
};
```

没有做一个“万能 `read/write/ioctl`”接口，因为：

- UART 是字节流；
- I2C 是地址 + 寄存器；
- CAN 是帧；
- 强行统一会让参数变成 `void*`，失去类型安全。

“通用”体现在**公共 `Status`/`ByteView`/`IBspDevice` 契约**，而不是把所有操作塞进一个函数。

## 适配器

`module/bsp/adapters.hpp`：

```cpp
class UartTxAdapter final : public IUart { ... };
class I2cTxAdapter  final : public II2c  { ... };
class CanTxAdapter  final : public ICan  { ... };
```

`.cpp` 里通过 `extern "C"` 调 C BSP：

```cpp
extern "C" {
#include "uart/bsp_uart_tx.h"
#include "i2c/bsp_i2c_tx.h"
#include "can/bsp_can_tx.h"
}

Status UartTxAdapter::write(ByteView data, std::uint32_t timeout_ms)
{
    if (data.empty() || data.size > 0xFFFFu) {
        return Status::InvalidArgument;
    }
    return mapUart(bsp_uart_tx_send(
        data.data, static_cast<std::uint16_t>(data.size), timeout_ms));
}
```

## 用法

```cpp
#include "bsp/adapters.hpp"

static module::bsp::UartTxAdapter uart;
static module::bsp::I2cTxAdapter  i2c;
static module::bsp::CanTxAdapter  can;

void app_init()
{
    if (uart.init() != module::bsp::Status::Ok) { /* ... */ }
    if (i2c.init()  != module::bsp::Status::Ok) { /* ... */ }
    if (can.init()  != module::bsp::Status::Ok) { /* ... */ }
}

void app_send()
{
    const std::uint8_t msg[] = "hello\r\n";
    uart.write({msg, sizeof(msg) - 1u}, 100u);

    const std::uint8_t wake = 0x00;
    i2c.writeReg(0x68u, 0x6Bu, {&wake, 1u}, 20u);

    module::bsp::CanFrame frame{};
    frame.id = 0x123u;
    frame.len = 8u;
    frame.data = {0x11, 0x22, 0x33, 0x44,
                  0x55, 0x66, 0x77, 0x88};
    can.send(frame, 10u);
}
```

也可以只依赖接口：

```cpp
void send_hello(module::bsp::IUart& uart)
{
    const std::uint8_t msg[] = "hello";
    uart.write({msg, sizeof(msg) - 1u}, 100u);
}
```

## 状态映射

以 UART 为例：

| C BSP | C++ `Status` |
|---|---|
| `BSP_UART_TX_OK` | `Ok` |
| `BSP_UART_TX_ERR_PARAM` | `InvalidArgument` |
| `BSP_UART_TX_ERR_INIT` | `InitFailed` |
| `BSP_UART_TX_ERR_BUSY` | `Busy` |
| `BSP_UART_TX_ERR_TIMEOUT` | `Timeout` |
| `BSP_UART_TX_ERR_BUS` | `BusError` |

I2C/CAN 同理，映射只在 `adapters.cpp` 内完成，接口层完全不出现 BSP 状态类型。

## 当前适配范围

| BSP | C++ 接口 | 说明 |
|---|---|---|
| `bsp_uart_tx` | `IUart` | 只发送 |
| `bsp_i2c_tx` | `II2c` | 只写 |
| `bsp_can_tx` | `ICan` | 只发标准数据帧，固定 8 字节 |

GPIO/PWM 的设备语义差异较大，暂时由 `module/servo` 等设备模块封装；  
如果以后要统一，可以按同样模式增加 `IGpio` / `IPwm`。

## CMake

```cmake
target_sources(${CMAKE_PROJECT_NAME} PRIVATE
    module/bsp/adapters.cpp
)

target_include_directories(${CMAKE_PROJECT_NAME} PRIVATE
    bsp
    module
)
```

C++ 源文件加入后，CMake 自动用 CXX 链接器：

```text
Building CXX object .../module/bsp/adapters.cpp.obj
Linking CXX executable NW.elf
```

## 注意

- `extern "C"` 只放在 `.cpp`，不要放进 `i_bus.hpp`；
- `IUart/II2c/ICan` 不 include BSP/HAL；
- `CanTxAdapter` 当前拒绝扩展帧、远程帧和 `len != 8`，因为 BSP 只支持标准 8 字节；
- `init()` 对“已经初始化”的 `BUSY` 做幂等处理：只要 `ready()` 为真，就返回 `Ok`；
- 没有异常/RTTI，失败全部用 `Status` 返回。
