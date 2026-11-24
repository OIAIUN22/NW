# UART 纯发送

`bsp_uart_tx` 只负责阻塞发送，不负责接收/DMA。

## 文件

```text
bsp/uart/
├─ bsp_uart_tx.h
├─ bsp_uart_tx.c
└─ README.md
```

## API

```c
bsp_uart_tx_status_t bsp_uart_tx_init(void);

bsp_uart_tx_status_t bsp_uart_tx_send(
    const uint8_t *data, uint16_t len,
    uint32_t timeout_ms);
```

## 用法

```c
#include "uart/bsp_uart_tx.h"

if (bsp_uart_tx_init() != BSP_UART_TX_OK) {
    Error_Handler();
}

const char msg[] = "hello\r\n";
bsp_uart_tx_send((const uint8_t *)msg, sizeof(msg) - 1u, 100u);
```

## CubeMX

`USART1`：PA9=TX，PA10=RX，115200 8N1。  
驱动使用 `huart1`，不重复初始化。

完整说明见 [../I2C_UART_TX_README.md](../I2C_UART_TX_README.md)。
