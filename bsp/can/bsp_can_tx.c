/**
  ******************************************************************************
  * @file    bsp_can_tx.c
  * @brief   STM32F1 bxCAN 纯发送驱动实现
  *
  * CubeMX 负责：
  *   - CAN1 时钟、PA11/PA12、位时间；
  *   - HAL_CAN_Init()（在 MX_CAN_Init() 中）。
  *
  * 本文件负责：
  *   - HAL_CAN_Start()；
  *   - 等空闲邮箱；
  *   - HAL_CAN_AddTxMessage() 发固定 8 字节；
  *   - 等发送完成/超时。
  *
  * 不接收、不配过滤器、不做协议解析、不依赖 FreeRTOS。
  ******************************************************************************
  */

#include "can/bsp_can_tx.h"

#include <stddef.h>

#include "stm32f1xx_hal.h"

/* CubeMX 在 main.c 中定义的全局句柄 */
extern CAN_HandleTypeDef hcan;

/* Private variables ---------------------------------------------------------*/

static uint8_t g_ready = 0u;

/* Exported functions -------------------------------------------------------*/

bsp_can_tx_status_t bsp_can_tx_init(void)
{
    if (g_ready != 0u) {
        return BSP_CAN_TX_ERR_BUSY;
    }

    /* MX_CAN_Init() 必须已经调用过；RESET 说明没初始化。 */
    if (hcan.State == HAL_CAN_STATE_RESET) {
        return BSP_CAN_TX_ERR_INIT;
    }

    /* CubeMX 只做 HAL_CAN_Init，不会自动 Start。 */
    if (hcan.State == HAL_CAN_STATE_READY) {
        if (HAL_CAN_Start(&hcan) != HAL_OK) {
            return BSP_CAN_TX_ERR_INIT;
        }
    } else if (hcan.State != HAL_CAN_STATE_LISTENING) {
        return BSP_CAN_TX_ERR_INIT;
    }

    g_ready = 1u;
    return BSP_CAN_TX_OK;
}

bsp_can_tx_status_t bsp_can_tx_send(uint32_t std_id,
                                    const uint8_t data[BSP_CAN_TX_DATA_LEN],
                                    uint32_t timeout_ms)
{
    if (g_ready == 0u) {
        return BSP_CAN_TX_ERR_INIT;
    }
    if (data == NULL || std_id > 0x7FFu) {
        return BSP_CAN_TX_ERR_PARAM;
    }

    const uint32_t start = HAL_GetTick();

    /* 1. 等一个空闲发送邮箱 */
    while (HAL_CAN_GetTxMailboxesFreeLevel(&hcan) == 0u) {
        if (timeout_ms == 0u) {
            return BSP_CAN_TX_ERR_BUSY;
        }
        if ((HAL_GetTick() - start) >= timeout_ms) {
            return BSP_CAN_TX_ERR_TIMEOUT;
        }
    }

    CAN_TxHeaderTypeDef header = {0};
    header.StdId = std_id;
    header.ExtId = 0u;
    header.IDE = CAN_ID_STD;
    header.RTR = CAN_RTR_DATA;
    header.DLC = BSP_CAN_TX_DATA_LEN; /* 固定 8 字节 */
    header.TransmitGlobalTime = DISABLE;

    uint32_t mailbox = 0u;
    if (HAL_CAN_AddTxMessage(&hcan, &header,
                             (uint8_t *)data, &mailbox) != HAL_OK) {
        return BSP_CAN_TX_ERR_BUS;
    }

    /* timeout_ms == 0：只入邮箱，立即返回；不保证总线上有节点 ACK。 */
    if (timeout_ms == 0u) {
        return BSP_CAN_TX_OK;
    }

    /* 2. 等发送完成：有 ACK 才会完成，无 ACK/总线错误会超时 */
    while (HAL_CAN_IsTxMessagePending(&hcan, mailbox) != 0u) {
        if ((HAL_CAN_GetError(&hcan) & HAL_CAN_ERROR_BOF) != 0u) {
            return BSP_CAN_TX_ERR_BUS;
        }
        if ((HAL_GetTick() - start) >= timeout_ms) {
            (void)HAL_CAN_AbortTxRequest(&hcan, mailbox);
            return BSP_CAN_TX_ERR_TIMEOUT;
        }
    }

    return BSP_CAN_TX_OK;
}

uint8_t bsp_can_tx_is_ready(void)
{
    return g_ready;
}
