/**
  ******************************************************************************
  * @file    bsp_i2c_tx.c
  * @brief   STM32F1 I2C1 纯发送驱动实现
  *
  * CubeMX 负责 I2C1 的时钟、PB6/PB7、100kHz、7-bit 和 HAL_I2C_Init()。
  * 本文件只做写操作和错误映射。
  ******************************************************************************
  */

#include "i2c/bsp_i2c_tx.h"

#include <stddef.h>

#include "stm32f1xx_hal.h"

/* CubeMX 在 main.c 中定义的全局句柄 */
extern I2C_HandleTypeDef hi2c1;

static uint8_t g_ready = 0u;

static bsp_i2c_tx_status_t map_hal(HAL_StatusTypeDef st)
{
    switch (st) {
    case HAL_OK:      return BSP_I2C_TX_OK;
    case HAL_TIMEOUT: return BSP_I2C_TX_ERR_TIMEOUT;
    case HAL_BUSY:    return BSP_I2C_TX_ERR_BUSY;
    default:          return BSP_I2C_TX_ERR_BUS;
    }
}

bsp_i2c_tx_status_t bsp_i2c_tx_init(void)
{
    if (g_ready != 0u) {
        return BSP_I2C_TX_ERR_BUSY;
    }
    if (HAL_I2C_GetState(&hi2c1) == HAL_I2C_STATE_RESET) {
        return BSP_I2C_TX_ERR_INIT;
    }

    g_ready = 1u;
    return BSP_I2C_TX_OK;
}

bsp_i2c_tx_status_t bsp_i2c_tx_write(uint8_t addr7,
                                     const uint8_t *data,
                                     uint16_t len,
                                     uint32_t timeout_ms)
{
    if (g_ready == 0u) {
        return BSP_I2C_TX_ERR_INIT;
    }
    if (addr7 > 0x7Fu || data == NULL || len == 0u) {
        return BSP_I2C_TX_ERR_PARAM;
    }

    /* HAL 使用 8 位地址：7 位地址左移 1 位 */
    return map_hal(HAL_I2C_Master_Transmit(
        &hi2c1, (uint16_t)(addr7 << 1), (uint8_t *)data, len, timeout_ms));
}

bsp_i2c_tx_status_t bsp_i2c_tx_write_reg(uint8_t addr7,
                                         uint8_t reg,
                                         const uint8_t *data,
                                         uint16_t len,
                                         uint32_t timeout_ms)
{
    if (g_ready == 0u) {
        return BSP_I2C_TX_ERR_INIT;
    }
    if (addr7 > 0x7Fu || data == NULL || len == 0u) {
        return BSP_I2C_TX_ERR_PARAM;
    }

    return map_hal(HAL_I2C_Mem_Write(
        &hi2c1, (uint16_t)(addr7 << 1), reg, I2C_MEMADD_SIZE_8BIT,
        (uint8_t *)data, len, timeout_ms));
}

uint8_t bsp_i2c_tx_is_ready(void)
{
    return g_ready;
}
