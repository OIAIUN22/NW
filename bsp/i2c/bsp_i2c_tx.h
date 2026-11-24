/**
  ******************************************************************************
  * @file    bsp_i2c_tx.h
  * @brief   STM32F1 I2C1 纯发送驱动（BSP 层）
  *
  * 只做：
  *   - 检查 CubeMX 已初始化的 hi2c1；
  *   - 向 7 位从机地址写一段字节；
  *   - 向从机寄存器写一段字节（传感器配置常用）。
  *
  * 不做：
  *   - 读取、中断、DMA、总线恢复；
  *   - 传感器 WHO_AM_I/单位换算/协议解析。
  *
  * CubeMX 已配置：
  *   I2C1: PB6=SCL, PB7=SDA, 100kHz, 7-bit
  ******************************************************************************
  */

#ifndef BSP_I2C_TX_H
#define BSP_I2C_TX_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    BSP_I2C_TX_OK = 0,
    BSP_I2C_TX_ERR_PARAM,
    BSP_I2C_TX_ERR_INIT,
    BSP_I2C_TX_ERR_BUSY,
    BSP_I2C_TX_ERR_TIMEOUT,
    BSP_I2C_TX_ERR_BUS,
} bsp_i2c_tx_status_t;

/**
  * @brief  检查 CubeMX 的 hi2c1 是否已初始化
  * @retval BSP_I2C_TX_OK        成功
  * @retval BSP_I2C_TX_ERR_INIT  hi2c1 处于 RESET，说明 MX_I2C1_Init() 没执行
  * @retval BSP_I2C_TX_ERR_BUSY  已经初始化过
  */
bsp_i2c_tx_status_t bsp_i2c_tx_init(void);

/**
  * @brief  向 7 位地址从机写一段字节（不含寄存器地址）
  * @param  addr7     7 位从机地址，例如 MPU6050 的 0x68
  * @param  data      数据
  * @param  len       字节数（1..65535）
  * @param  timeout_ms 总超时
  */
bsp_i2c_tx_status_t bsp_i2c_tx_write(uint8_t addr7,
                                     const uint8_t *data,
                                     uint16_t len,
                                     uint32_t timeout_ms);

/**
  * @brief  向从机的 8 位寄存器地址写一段字节
  * @param  addr7     7 位从机地址
  * @param  reg       8 位寄存器地址
  * @param  data      数据
  * @param  len       字节数（1..65535）
  * @param  timeout_ms 总超时
  */
bsp_i2c_tx_status_t bsp_i2c_tx_write_reg(uint8_t addr7,
                                         uint8_t reg,
                                         const uint8_t *data,
                                         uint16_t len,
                                         uint32_t timeout_ms);

/**
  * @brief  是否已检查/初始化
  */
uint8_t bsp_i2c_tx_is_ready(void);

#ifdef __cplusplus
}
#endif

#endif /* BSP_I2C_TX_H */
