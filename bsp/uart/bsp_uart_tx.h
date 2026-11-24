/**
  ******************************************************************************
  * @file    bsp_uart_tx.h
  * @brief   STM32F1 USART1 纯发送驱动（BSP 层）
  *
  * 只做：
  *   - 检查 CubeMX 已初始化的 huart1；
  *   - 阻塞发送一段字节；
  *   - 返回明确的超时/忙/总线错误。
  *
  * 不做：
  *   - 接收、中断、DMA、环形缓冲；
  *   - printf 重定向、协议解析、业务日志。
  *
  * CubeMX 已配置：
  *   USART1: PA9=TX, PA10=RX, 115200 8N1
  ******************************************************************************
  */

#ifndef BSP_UART_TX_H
#define BSP_UART_TX_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    BSP_UART_TX_OK = 0,
    BSP_UART_TX_ERR_PARAM,
    BSP_UART_TX_ERR_INIT,
    BSP_UART_TX_ERR_BUSY,
    BSP_UART_TX_ERR_TIMEOUT,
    BSP_UART_TX_ERR_BUS,
} bsp_uart_tx_status_t;

/**
  * @brief  检查 CubeMX 的 huart1 是否已初始化
  * @retval BSP_UART_TX_OK        成功
  * @retval BSP_UART_TX_ERR_INIT  huart1 处于 RESET，说明 MX_USART1_UART_Init() 没执行
  * @retval BSP_UART_TX_ERR_BUSY  已经初始化过
  */
bsp_uart_tx_status_t bsp_uart_tx_init(void);

/**
  * @brief  阻塞发送一段字节
  * @param  data       数据指针
  * @param  len        字节数（1..65535）
  * @param  timeout_ms 总超时
  * @retval BSP_UART_TX_OK        成功
  * @retval BSP_UART_TX_ERR_PARAM data 为空或 len 为 0/超出 uint16
  * @retval BSP_UART_TX_ERR_INIT  未初始化
  * @retval BSP_UART_TX_ERR_BUSY  串口正忙
  * @retval BSP_UART_TX_ERR_TIMEOUT 发送超时
  * @retval BSP_UART_TX_ERR_BUS   其他 HAL 错误
  */
bsp_uart_tx_status_t bsp_uart_tx_send(const uint8_t *data,
                                      uint16_t len,
                                      uint32_t timeout_ms);

/**
  * @brief  是否已检查/初始化
  */
uint8_t bsp_uart_tx_is_ready(void);

#ifdef __cplusplus
}
#endif

#endif /* BSP_UART_TX_H */
