# SG90 舵机 PWM 驱动

`bsp_sg90` 只负责：

- 初始化 TIM2 CH1/CH2 为 50Hz PWM；
- 设置脉宽 `500..2500us`；
- 停止某个通道。

**角度—脉宽换算在 `module/servo/sg90_angle`，不在 BSP。**  
不负责舵机电源、机械限位、闭环控制。

## 文件

```text
bsp/pwm/
├─ bsp_sg90.h
├─ bsp_sg90.c
└─ README.md
```

## 引脚

| 通道 | 引脚 | 定时器 |
|---|---|---|
| CH1 | PA0 | TIM2_CH1 |
| CH2 | PA1 | TIM2_CH2 |

两个 SG90 可以分别接 PA0、PA1。  
**信号线只接 PWM；舵机电源必须单独 5V，和 MCU 共地。**

## 时序

```text
PWM 频率 = 50Hz，周期 20ms
0°   ≈ 500us
90°  ≈ 1500us
180° ≈ 2500us
```

当前 `NW` 工程 HSI 8MHz、APB1 不分频：

```text
TIM2_CLK = 8MHz
PSC = 7       -> 1MHz 计数
ARR = 20000-1 -> 50Hz
CCR = 500..2500 -> 0.5..2.5ms
```

驱动会根据 `HAL_RCC_GetPCLK1Freq()` 和 APB1 分频自动算 PSC，不是写死 7。

## API

```c
typedef enum {
    BSP_SG90_CH1 = 0,   /* PA0 / TIM2_CH1 */
    BSP_SG90_CH2 = 1,   /* PA1 / TIM2_CH2 */
} bsp_sg90_channel_t;

typedef enum {
    BSP_SG90_OK = 0,
    BSP_SG90_ERR_PARAM,
    BSP_SG90_ERR_INIT,
    BSP_SG90_ERR_BUSY,
    BSP_SG90_ERR_STATE,
} bsp_sg90_status_t;

bsp_sg90_status_t bsp_sg90_init(void);
bsp_sg90_status_t bsp_sg90_set_pulse_us(bsp_sg90_channel_t ch, uint16_t us);
bsp_sg90_status_t bsp_sg90_disable(bsp_sg90_channel_t ch);
uint8_t bsp_sg90_is_ready(void);
```

## 用法

```c
#include "pwm/bsp_sg90.h"

if (bsp_sg90_init() != BSP_SG90_OK) {
    Error_Handler();
}

/* 两个舵机回中位：1.5ms */
bsp_sg90_set_pulse_us(BSP_SG90_CH1, 1500u);
bsp_sg90_set_pulse_us(BSP_SG90_CH2, 1500u);

/* 扫动：脉宽从 1000us 到 2000us */
for (uint16_t us = 1000u; us <= 2000u; us += 10u) {
    bsp_sg90_set_pulse_us(BSP_SG90_CH1, us);
    HAL_Delay(20);
}
```

> 角度换算请用 module 的 `Sg90Servo::setAngle()`。  
> 上电先回中位，再小角度测试。不要一上来 `0 → 180` 猛甩，容易堵转/过流。

## 电气注意

- SG90 用 **5V 独立电源**，不要从 MCU 3.3V 取电；
- 两个舵机同时动，电流可能几百 mA 到 1A；
- 电源和 MCU **必须共地**；
- 电源并 100µF 电解 + 0.1µF 陶瓷；
- 信号线 3.3V PWM 通常可以驱动 SG90 信号输入；
- 机械上先空载测试，再装负载。

## 常见坑

1. **用 3.3V 给 SG90 供电**：带不动/复位。
2. **不共地**：PWM 有信号但舵机乱抖。
3. **50Hz 配错**：PSC/ARR 算错，舵机不动或抖。
4. **角度越界**：module 的 `Sg90Servo::setAngle()` 返回 `InvalidArgument`。
5. **脉宽超出 500..2500us**：BSP 返回 `BSP_SG90_ERR_PARAM`。
6. **和 CubeMX 同时配置 TIM2**：会重复初始化；本驱动自己配 TIM2，CubeMX 不要再开 TIM2 PWM。
7. **CubeMX 重新生成后 HAL TIM 被关掉**：本工程手动打开了 `HAL_TIM_MODULE_ENABLED` 并加入 `stm32f1xx_hal_tim.c`；重新生成后检查这两处，否则 `bsp_sg90.c` 会编译不过。

## CMake

```cmake
target_sources(${CMAKE_PROJECT_NAME} PRIVATE
    bsp/pwm/bsp_sg90.c
)
```

头文件通过 `bsp` 根目录包含：

```c
#include "pwm/bsp_sg90.h"
```
