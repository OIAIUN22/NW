# BSP GPIO 纯驱动

> CAN 纯发送见 [CAN_TX_README.md](CAN_TX_README.md)。  
> I2C / UART 纯发送见 [I2C_UART_TX_README.md](I2C_UART_TX_README.md)。

这是 `NW` 项目的第一个 BSP 驱动：只封装 **STM32F1 GPIO**，不包含 LED、按键、业务逻辑，也不依赖 FreeRTOS / module / app。

## 文件

```text
bsp/
├─ bsp_gpio.h      # 对外接口
├─ bsp_gpio.c      # HAL 实现
└─ README.md
```

## 设计目标

- **纯驱动**：只有 `init / deinit / read / write / toggle`；
- **可多实例**：每个 `bsp_gpio_t` 保存自己的 port/pin，不写死 LED；
- **错误可见**：参数错误、端口不支持、未初始化，都有明确返回值；
- **不动态分配**：实例由调用者用静态/全局变量提供；
- **自动开时钟**：按 `GPIOA..GPIOE` 使能对应 RCC 时钟，避免“忘了开时钟”；
- **输出先写初值再配置**：减少上电毛刺；
- **不阻塞**：驱动内部没有 `HAL_Delay`，延时由上层决定。

## API

```c
bsp_gpio_status_t bsp_gpio_init(bsp_gpio_t *self,
                                const bsp_gpio_config_t *config);
void              bsp_gpio_deinit(bsp_gpio_t *self);
bsp_gpio_status_t bsp_gpio_write(bsp_gpio_t *self, bsp_gpio_level_t level);
bsp_gpio_status_t bsp_gpio_toggle(bsp_gpio_t *self);
bsp_gpio_status_t bsp_gpio_read(const bsp_gpio_t *self,
                                bsp_gpio_level_t *level);
```

状态码：

| 状态 | 含义 |
|---|---|
| `BSP_GPIO_OK` | 成功 |
| `BSP_GPIO_ERR_PARAM` | 参数为空、pin 为 0、level 非法 |
| `BSP_GPIO_ERR_PORT` | 不支持的 GPIO 端口 |
| `BSP_GPIO_ERR_STATE` | 未初始化，或对输入/模拟引脚执行写/翻转 |

## 用法：点亮/翻转 Blue Pill 的 PC13 LED

F103C8T6 最小系统板的 PC13 LED 通常是**低电平点亮**。  
下面例子先输出高电平（灭），再每 500ms 翻转一次。

```c
#include "gpio/bsp_gpio.h"

static bsp_gpio_t g_led;

static bsp_gpio_status_t led_init(void)
{
    const bsp_gpio_config_t cfg = {
        .port = GPIOC,
        .pin = GPIO_PIN_13,
        .mode = BSP_GPIO_MODE_OUTPUT_PP,
        .pull = BSP_GPIO_PULL_NONE,
        .speed = BSP_GPIO_SPEED_LOW,
        .initial = BSP_GPIO_HIGH,   /* 低电平亮：先灭 */
    };
    return bsp_gpio_init(&g_led, &cfg);
}

int main(void)
{
    HAL_Init();
    SystemClock_Config();

    if (led_init() != BSP_GPIO_OK) {
        Error_Handler();
    }

    for (;;) {
        (void)bsp_gpio_toggle(&g_led);
        HAL_Delay(500);
    }
}
```

## 为什么不用 `HAL_GPIO_TogglePin` 直接写业务

直接写：

```c
HAL_GPIO_TogglePin(GPIOC, GPIO_PIN_13);
```

能跑，但：

- 引脚写死在业务里，换板子要改业务；
- 没有统一的错误返回；
- 没有“实例”概念，多个 GPIO 容易混；
- 后续无法在 PC 上用假实现测试。

BSP 驱动把“哪个端口、哪个引脚、什么模式”收进配置，业务只持有 `bsp_gpio_t`。

## 编译接入

已在 `CMakeLists.txt` 加入：

```cmake
target_sources(${CMAKE_PROJECT_NAME} PRIVATE
    bsp/gpio/bsp_gpio.c
)

target_include_directories(${CMAKE_PROJECT_NAME} PRIVATE
    bsp
)
```

编译：

```bash
cmake --build build/Debug
```

当前已编译通过，`NW.elf` 生成正常。  
`main.c` **没有改动**，仍是原来的 HAL 点灯逻辑；要验证本驱动，把上面的示例贴进 `main.c` 的 `USER CODE` 区域即可。

## 常见坑

1. **忘记开 GPIO 时钟**：本驱动已自动使能，但如果你自己写 HAL，必须 `__HAL_RCC_GPIOx_CLK_ENABLE()`。
2. **PC13 低电平亮**：`initial = BSP_GPIO_HIGH` 是灭，别以为写反了。
3. **输入模式又去 write/toggle**：驱动会返回 `BSP_GPIO_ERR_STATE`。
4. **把 `GPIO_PIN_13` 当成引脚号 13**：它是位掩码 `1 << 13`，不要自己写 `13`。
5. **在中断里 `HAL_Delay`**：驱动没有延时，但上层也不该在 ISR 里延时。

## 下一份驱动

按同样模板继续写：

- `bsp_uart`：阻塞 + DMA/中断，环形缓冲；
- `bsp_i2c`：阻塞 + 中断，总线恢复；
- `bsp_can`：阻塞发送 + 中断接收，过滤器/bus-off；
- `bsp_timer`：1ms tick / PWM。

每一份都守同一条边界：**BSP 只碰 HAL，不写业务。**
