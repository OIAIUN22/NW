# BSP 目录

底层驱动按外设/协议分目录，方便扩展和查找：

```text
bsp/
├─ gpio/     GPIO 输入/输出（LED、按键、激光）
├─ can/      CAN 纯发送
├─ i2c/      I2C 纯写
├─ uart/     UART 纯发送
└─ pwm/      SG90 舵机 PWM
```

| 目录 | 内容 |
|---|---|
| [gpio](gpio/README.md) | `bsp_gpio`：初始化、读、写、翻转 |
| [can](can/README.md) | `bsp_can_tx`：500kbps 标准帧，固定 8 字节 |
| [i2c](i2c/README.md) | `bsp_i2c_tx`：7 位地址写、寄存器写 |
| [uart](uart/README.md) | `bsp_uart_tx`：USART1 阻塞发送 |
| [pwm](pwm/README.md) | `bsp_sg90`：TIM2 CH1/CH2，50Hz 舵机 PWM |

> I2C/UART 的详细说明暂时放在 [I2C_UART_TX_README.md](I2C_UART_TX_README.md)；  
> 后续会拆成 `i2c/README.md` 和 `uart/README.md`。

## 约定

- BSP 层可以直接 include HAL；
- module/app 不直接 include BSP 具体头文件，只通过接口/组合根使用；
- 每份驱动都返回明确状态码，不静默失败；
- 每份驱动都只做“外设能力”，不写业务。
