# BSP I2C / UART 纯发送驱动

这两份驱动和 CAN 纯发送驱动保持同一风格：

- 只负责“发送”；
- 不接收、不做协议、不依赖 FreeRTOS / module / app；
- 使用 CubeMX 已生成的 `hi2c1` / `huart1`；
- 初始化函数只检查 CubeMX 是否初始化成功，不重复配置外设；
- 所有失败都有明确 `status`。

## 文件

```text
bsp/
├─ i2c/bsp_i2c_tx.h / .c
├─ uart/bsp_uart_tx.h / .c
└─ I2C_UART_TX_README.md
```

CubeMX 已配置：

| 外设 | 引脚 | 参数 |
|---|---|---|
| I2C1 | PB6=SCL，PB7=SDA | 100 kHz，7-bit |
| USART1 | PA9=TX，PA10=RX | 115200，8N1 |

`main.c` 中已有：

```c
I2C_HandleTypeDef hi2c1;
UART_HandleTypeDef huart1;

MX_I2C1_Init();
MX_USART1_UART_Init();
```

---

## 1. UART 纯发送

### API

```c
typedef enum {
    BSP_UART_TX_OK = 0,
    BSP_UART_TX_ERR_PARAM,
    BSP_UART_TX_ERR_INIT,
    BSP_UART_TX_ERR_BUSY,
    BSP_UART_TX_ERR_TIMEOUT,
    BSP_UART_TX_ERR_BUS,
} bsp_uart_tx_status_t;

bsp_uart_tx_status_t bsp_uart_tx_init(void);

bsp_uart_tx_status_t bsp_uart_tx_send(
    const uint8_t *data,
    uint16_t len,
    uint32_t timeout_ms);

uint8_t bsp_uart_tx_is_ready(void);
```

### 用法

```c
#include "uart/bsp_uart_tx.h"

if (bsp_uart_tx_init() != BSP_UART_TX_OK) {
    Error_Handler();
}

const char msg[] = "hello\r\n";
bsp_uart_tx_status_t st =
    bsp_uart_tx_send((const uint8_t *)msg, sizeof(msg) - 1u, 100u);
```

- 使用 `HAL_UART_Transmit`，阻塞发送；
- 长度是 `uint16_t`，一次最多 65535 字节；
- 超时、忙、其他 HAL 错误会返回不同状态；
- 没有 DMA/中断接收，后续需要时单独加 `bsp_uart_rx` 或扩展。

### 接线

```text
MCU PA9  (TX) → USB-TTL RX
MCU PA10 (RX) → USB-TTL TX
GND          → GND
```

- 串口助手：115200，8N1，无流控；
- 不要用 5V TTL 直连 3.3V MCU 的 RX；
- TX/RX 必须交叉。

---

## 2. I2C 纯发送

### API

```c
typedef enum {
    BSP_I2C_TX_OK = 0,
    BSP_I2C_TX_ERR_PARAM,
    BSP_I2C_TX_ERR_INIT,
    BSP_I2C_TX_ERR_BUSY,
    BSP_I2C_TX_ERR_TIMEOUT,
    BSP_I2C_TX_ERR_BUS,
} bsp_i2c_tx_status_t;

bsp_i2c_tx_status_t bsp_i2c_tx_init(void);

bsp_i2c_tx_status_t bsp_i2c_tx_write(
    uint8_t addr7,
    const uint8_t *data,
    uint16_t len,
    uint32_t timeout_ms);

bsp_i2c_tx_status_t bsp_i2c_tx_write_reg(
    uint8_t addr7,
    uint8_t reg,
    const uint8_t *data,
    uint16_t len,
    uint32_t timeout_ms);

uint8_t bsp_i2c_tx_is_ready(void);
```

### 用法：写寄存器

以 MPU6050 为例（7 位地址 `0x68`，`PWR_MGMT_1` 寄存器 `0x6B`）：

```c
#include "i2c/bsp_i2c_tx.h"

if (bsp_i2c_tx_init() != BSP_I2C_TX_OK) {
    Error_Handler();
}

uint8_t wake = 0x00;
bsp_i2c_tx_status_t st =
    bsp_i2c_tx_write_reg(0x68u, 0x6Bu, &wake, 1u, 20u);
```

### 用法：直接写一段字节

```c
uint8_t cmd[2] = {0x01, 0x02};
bsp_i2c_tx_write(0x68u, cmd, sizeof(cmd), 20u);
```

- `addr7` 是 7 位地址，驱动内部会 `<< 1`；
- `write_reg` 使用 `HAL_I2C_Mem_Write`，寄存器地址固定 8 位；
- 只写不读；读传感器要另写 `bsp_i2c_rx`；
- 没有总线恢复；若从机拉死 SDA，需要后续加 9 clocks 恢复。

### 接线

```text
MCU PB6 (SCL) → 模块 SCL
MCU PB7 (SDA) → 模块 SDA
3.3V          → 模块 VCC
GND           → 模块 GND
```

- SCL/SDA 需要上拉（模块常自带 4.7kΩ；没有就外接）；
- 先 100 kHz 调通，再尝试 400 kHz；
- 线尽量短；
- 7 位地址不要写成 8 位地址，驱动会自己左移。

---

## 3. 接到 `main.c`

在 `USER CODE BEGIN 2` 中：

```c
#include "i2c/bsp_i2c_tx.h"
#include "uart/bsp_uart_tx.h"

if (bsp_i2c_tx_init() != BSP_I2C_TX_OK) {
    Error_Handler();
}
if (bsp_uart_tx_init() != BSP_UART_TX_OK) {
    Error_Handler();
}
```

> `MX_I2C1_Init()` 和 `MX_USART1_UART_Init()` 必须已经在 `main()` 中调用；  
> 这两个驱动不会重复初始化外设。

## 4. 设计边界

| 做 | 不做 |
|---|---|
| 检查 CubeMX 句柄状态 | 重新配置时钟/引脚 |
| 阻塞写 I2C/UART | 接收 |
| 返回明确状态码 | DMA/中断/环形缓冲 |
| 7 位地址自动左移 | 传感器单位换算 |
| 固定超时 | 总线恢复/协议解析 |

## 5. 常见坑

1. **没有调用 `MX_I2C1_Init()` / `MX_USART1_UART_Init()`**：`init()` 返回 `ERR_INIT`。
2. **I2C 地址没左移**：驱动已经处理，传 7 位地址即可。
3. **I2C 没有上拉**：一直 NACK。
4. **UART TX/RX 没交叉**：收不到/发不出。
5. **UART 用 5V TTL 直连 3.3V**：可能损伤 MCU。
6. **`len` 超过 65535**：`uint16_t` 会截断；本驱动参数就是 `uint16_t`，调用方自己保证。
7. **在中断里调用阻塞发送**：会卡死；这些接口只应在任务/主循环里调用。

## 6. 编译

```bash
cmake --build build/Debug
```

`CMakeLists.txt` 已加入：

```cmake
target_sources(${CMAKE_PROJECT_NAME} PRIVATE
    bsp/gpio/bsp_gpio.c
    bsp/can/bsp_can_tx.c
    bsp/i2c/bsp_i2c_tx.c
    bsp/uart/bsp_uart_tx.c
)
```
