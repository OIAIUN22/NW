# BSP CAN 纯发送驱动

这份驱动只做一件事：

> **把 8 个字节按标准帧发到 CAN 总线上。**

它不接收、不配过滤器、不做协议解析、不依赖 FreeRTOS / module / app。  
CubeMX 已负责 CAN1 的时钟、PA11/PA12 和位时间；本驱动只负责启动、等邮箱、发送、等完成。

## 文件

```text
bsp/
├─ bsp_can_tx.h      # 对外接口
├─ bsp_can_tx.c      # HAL 实现
└─ CAN_TX_README.md
```

## 分工

```text
CubeMX / MX_CAN_Init()
  ├─ 开 CAN1 时钟
  ├─ 配 PA11 = CAN_RX、PA12 = CAN_TX
  ├─ 配 500kbps 位时间
  └─ HAL_CAN_Init(&hcan)

bsp_can_tx_init()
  └─ HAL_CAN_Start(&hcan)

bsp_can_tx_send()
  ├─ 等空闲邮箱
  ├─ HAL_CAN_AddTxMessage(DLC=8)
  └─ 等发送完成/超时
```

## API

```c
#define BSP_CAN_TX_DATA_LEN 8u

typedef enum {
    BSP_CAN_TX_OK = 0,
    BSP_CAN_TX_ERR_PARAM,
    BSP_CAN_TX_ERR_INIT,
    BSP_CAN_TX_ERR_BUSY,
    BSP_CAN_TX_ERR_TIMEOUT,
    BSP_CAN_TX_ERR_BUS,
} bsp_can_tx_status_t;

bsp_can_tx_status_t bsp_can_tx_init(void);

bsp_can_tx_status_t bsp_can_tx_send(
    uint32_t std_id,
    const uint8_t data[BSP_CAN_TX_DATA_LEN],
    uint32_t timeout_ms);

uint8_t bsp_can_tx_is_ready(void);
```

## 用法

```c
#include "can/bsp_can_tx.h"

static const uint8_t kData[8] = {
    0x11, 0x22, 0x33, 0x44,
    0x55, 0x66, 0x77, 0x88,
};

int main(void)
{
    HAL_Init();
    SystemClock_Config();

    MX_GPIO_Init();
    MX_I2C1_Init();
    MX_USART1_UART_Init();
    MX_CAN_Init();              /* CubeMX 生成，必须调用 */

    if (bsp_can_tx_init() != BSP_CAN_TX_OK) {
        Error_Handler();
    }

    for (;;) {
        bsp_can_tx_status_t st =
            bsp_can_tx_send(0x123u, kData, 10u);

        if (st != BSP_CAN_TX_OK) {
            /* 超时/总线错误，由上层决定怎么处理 */
        }

        HAL_Delay(100);
    }
}
```

- `std_id` 只支持 11 位标准帧，范围 `0x000..0x7FF`；
- `data` 必须指向 8 个字节；
- `timeout_ms == 0`：只保证写入发送邮箱，不等待 ACK；
- `timeout_ms > 0`：等发送完成；没有第二节点 ACK 时会超时。

## CubeMX 配置

当前 `NW.ioc` 中：

- `CAN`：500 kbps；
- `PA11 = CAN_RX`；
- `PA12 = CAN_TX`；
- `CAN` 的 `Prescaler=1`、`BS1=CAN_BS1_13TQ`、`BS2=CAN_BS2_2TQ`；
- 8MHz PCLK1 下：`8MHz / 1 / (1+13+2) = 500kbps`。

CubeMX 生成：

- `CAN_HandleTypeDef hcan;`
- `MX_CAN_Init()`；
- `HAL_CAN_MspInit()`：使能 CAN1/GPIOA 时钟，配 PA11/PA12。

**本驱动不再自己配置 GPIO/位时间**，避免和 `MX_CAN_Init()` 重复初始化。

## 接线

| MCU | 方向 | 接什么 |
|---|---|---|
| PA11 | CAN_RX | 收发器 RXD |
| PA12 | CAN_TX | 收发器 TXD |
| 3.3V/5V | 电源 | 按收发器要求 |
| GND | 地 | 必须共地 |

```text
MCU PA11/PA12 → CAN 收发器 → CAN_H / CAN_L → 第二节点
总线两端各 120Ω
```

没有收发器，PA11/PA12 只是普通逻辑信号，不会产生 CAN 差分电平。  
没有第二节点/没有 ACK，`timeout_ms > 0` 的发送会超时，这是正常现象。

## 设计边界

| 做 | 不做 |
|---|---|
| HAL_CAN_Start | 接收帧 |
| 等邮箱/等完成/超时 | 配过滤器 |
| 发标准数据帧，DLC=8 | 电机协议/设备 ID |
| 返回明确状态码 | FreeRTOS 队列/任务 |
| 不重复配置 CubeMX 外设 | 业务日志/状态机 |

## 常见坑

1. **没有调用 `MX_CAN_Init()`**：`hcan.State` 是 RESET，`bsp_can_tx_init()` 返回 `ERR_INIT`。
2. **没有收发器**：CAN_TX/RX 只是逻辑电平，总线不会有差分信号。
3. **没有 120Ω**：短距离可能偶尔能通，长距离必挂。
4. **没有第二节点**：发送没有 ACK，`timeout_ms > 0` 会超时。
5. **双方波特率不一致**：错误帧、bus-off。
6. **把标准 ID 写成超过 0x7FF**：驱动返回 `BSP_CAN_TX_ERR_PARAM`。
7. **`timeout_ms=0` 却以为已经发到总线**：它只保证进邮箱，不保证 ACK。
8. **CubeMX 重新生成后覆盖 `main.c`**：`MX_CAN_Init()` 会保留；用户代码要放在 `USER CODE` 区。

## 编译

```bash
cmake --build build/Debug
```

CubeMX 已经把：

- `Core/Inc/stm32f1xx_hal_conf.h` 里的 `HAL_CAN_MODULE_ENABLED` 打开；
- `Drivers/STM32F1xx_HAL_Driver/Src/stm32f1xx_hal_can.c` 加入构建；
- `cmake/stm32cubemx/CMakeLists.txt` 加入 HAL CAN 源文件。

`CMakeLists.txt` 中已加入：

```cmake
target_sources(${CMAKE_PROJECT_NAME} PRIVATE
    bsp/gpio/bsp_gpio.c
    bsp/can/bsp_can_tx.c
)
```
