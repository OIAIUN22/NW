# Module 层

Module 层分成两类：

```text
module/
├─ bsp/          # 面向 BSP 的通用 C++17 接口 + C 适配器
├─ interfaces/   # 设备级接口（如 IServo）
├─ servo/        # 具体设备模块（如 SG90）
└─ README.md
```

## 1. 面向 BSP 的通用接口（重点）

`module/bsp/` 把 C 编译的 BSP 驱动适配成 C++17 能力接口：

```text
module::bsp::IUart  ◄── UartTxAdapter  ── extern "C" ──► bsp_uart_tx.c
module::bsp::II2c   ◄── I2cTxAdapter   ── extern "C" ──► bsp_i2c_tx.c
module::bsp::ICan   ◄── CanTxAdapter   ── extern "C" ──► bsp_can_tx.c
```

公共类型：

- `module::bsp::Status`：统一错误码；
- `module::bsp::ByteView`：C++17 的“指针 + 长度”，替代 C++20 `std::span`；
- `module::bsp::CanFrame`：标准帧；
- `module::bsp::IBspDevice`：`init/ready/name` 公共契约。

详细说明见 [bsp/README.md](bsp/README.md)。

## 2. 设备级接口

`module/interfaces/i_servo.hpp` 是设备能力接口，不是 BSP 通用接口：

```cpp
module::IServo
  ▲
  │ 实现
module::Sg90Servo  ── extern "C" ──► bsp_sg90.c
```

`servo/` 是具体设备模块，适合放“SG90 的角度/脉宽/使能”这类设备语义。

## 3. 分层边界

| 层 | 应该知道 | 不应该知道 |
|---|---|---|
| `module/bsp` | C BSP 函数、C 状态码 | 具体设备协议、HAL 细节 |
| `module/interfaces` | 设备能力 | BSP 头、HAL |
| `module/servo` | SG90 语义、`IServo` | HAL、具体引脚 |
| `app` | `IUart/II2c/ICan/IServo` | `extern "C"`、BSP 状态码 |

## 4. C/C++ 链接规则

- BSP 用 C 编译器编译，符号是 C linkage；
- C++ adapter 的 `.cpp` 用 `extern "C"` 包含 C 头；
- C++ 接口头文件不 include BSP/HAL；
- CMake 同时启用 C/C++，有 `.cpp` 后自动用 CXX 链接器。

## 5. 用法示例

```cpp
#include "bsp/adapters.hpp"

static module::bsp::UartTxAdapter uart;
static module::bsp::I2cTxAdapter  i2c;
static module::bsp::CanTxAdapter  can;

void app_init()
{
    uart.init();
    i2c.init();
    can.init();
}

void app_send()
{
    const std::uint8_t msg[] = "hello";
    uart.write({msg, sizeof(msg) - 1u}, 100u);

    module::bsp::CanFrame f{};
    f.id = 0x123u;
    f.len = 8u;
    f.data = {0x11, 0x22, 0x33, 0x44,
              0x55, 0x66, 0x77, 0x88};
    can.send(f, 10u);
}
```

## 6. CMake

```cmake
target_sources(${CMAKE_PROJECT_NAME} PRIVATE
    module/bsp/adapters.cpp
    module/servo/sg90_servo.cpp
)

target_include_directories(${CMAKE_PROJECT_NAME} PRIVATE
    bsp
    module
)
```
