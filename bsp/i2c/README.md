# I2C 纯发送

`bsp_i2c_tx` 只负责写，不负责读。

## 文件

```text
bsp/i2c/
├─ bsp_i2c_tx.h
├─ bsp_i2c_tx.c
└─ README.md
```

## API

```c
bsp_i2c_tx_status_t bsp_i2c_tx_init(void);

bsp_i2c_tx_status_t bsp_i2c_tx_write(
    uint8_t addr7, const uint8_t *data,
    uint16_t len, uint32_t timeout_ms);

bsp_i2c_tx_status_t bsp_i2c_tx_write_reg(
    uint8_t addr7, uint8_t reg,
    const uint8_t *data, uint16_t len,
    uint32_t timeout_ms);
```

## 用法

```c
#include "i2c/bsp_i2c_tx.h"

if (bsp_i2c_tx_init() != BSP_I2C_TX_OK) {
    Error_Handler();
}

uint8_t wake = 0x00;
bsp_i2c_tx_write_reg(0x68u, 0x6Bu, &wake, 1u, 20u);
```

- `addr7` 是 7 位地址，驱动内部会 `<< 1`；
- `write_reg` 使用 `HAL_I2C_Mem_Write`，寄存器地址 8 位；
- 只写不读；MPU6050 需要另加 `bsp_i2c_rx`。

完整说明见 [../I2C_UART_TX_README.md](../I2C_UART_TX_README.md)。

## CubeMX

`I2C1`：PB6=SCL，PB7=SDA，100kHz，7-bit。  
驱动使用 `hi2c1`，不重复初始化。
