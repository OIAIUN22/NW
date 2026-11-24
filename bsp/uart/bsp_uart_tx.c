/**
  ******************************************************************************
  * @file    bsp_uart_tx.c
  * @brief   STM32F1 USART1 纯发送驱动实现
  *
  * CubeMX 负责 USART1 的时钟、PA9/PA10、115200 8N1 和 HAL_UART_Init()。
  * 本文件只做阻塞发送和错误映射。
  ******************************************************************************
  */

#include "uart/bsp_uart_tx.h"

#include <stddef.h>

#include "stm32f1xx_hal.h"

/* CubeMX 在 main.c 中定义的全局句柄 */
extern UART_HandleTypeDef huart1;

static uint8_t g_ready = 0u;

bsp_uart_tx_status_t bsp_uart_tx_init(void)
{
    if (g_ready != 0u) {
        return BSP_UART_TX_ERR_BUSY;
    }
    if (HAL_UART_GetState(&huart1) == HAL_UART_STATE_RESET) {
        return BSP_UART_TX_ERR_INIT;
    }

    g_ready = 1u;
    return BSP_UART_TX_OK;
}

bsp_uart_tx_status_t bsp_uart_tx_send(const uint8_t *data,
                                      uint16_t len,
                                      uint32_t timeout_ms)
{
    if (g_ready == 0u) {
        return BSP_UART_TX_ERR_INIT;
    }
    if (data == NULL || len == 0u) {
        return BSP_UART_TX_ERR_PARAM;
    }

    const HAL_StatusTypeDef st =
        HAL_UART_Transmit(&huart1, (uint8_t *)data, len, timeout_ms);

    switch (st) {
    case HAL_OK:      return BSP_UART_TX_OK;
    case HAL_TIMEOUT: return BSP_UART_TX_ERR_TIMEOUT;
    case HAL_BUSY:    return BSP_UART_TX_ERR_BUSY;
    default:          return BSP_UART_TX_ERR_BUS;
    }
}

uint8_t bsp_uart_tx_is_ready(void)
{
    return g_ready;
}
