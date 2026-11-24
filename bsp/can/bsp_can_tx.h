/**
  ******************************************************************************
  * @file    bsp_can_tx.h
  * @brief   STM32F1 bxCAN 纯发送驱动（BSP 层）
  *
  * 这份驱动只做一件事：
  *   把 8 个字节按标准帧发到 CAN 总线上。
  *
  * 不包含：
  *   - 接收、过滤器、队列、环形缓冲；
  *   - 电机协议、设备 ID、周期任务；
  *   - FreeRTOS、module、app 业务。
  *
  * 外设初始化分工：
  *   - CubeMX 的 MX_CAN_Init()：时钟、PA11/PA12、位时间、HAL_CAN_Init；
  *   - 本驱动：HAL_CAN_Start、等邮箱、发 8 字节、等完成/超时。
  *
  * 引脚（STM32F103C8T6 默认 CAN1）：
  *   PA11 = CAN_RX
  *   PA12 = CAN_TX
  * 需要外部 CAN 收发器（TJA1050 / SN65HVD230 等）和 120Ω 终端电阻。
  ******************************************************************************
  */

#ifndef BSP_CAN_TX_H
#define BSP_CAN_TX_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define BSP_CAN_TX_DATA_LEN 8u

typedef enum {
    BSP_CAN_TX_OK = 0,
    BSP_CAN_TX_ERR_PARAM,
    BSP_CAN_TX_ERR_INIT,
    BSP_CAN_TX_ERR_BUSY,
    BSP_CAN_TX_ERR_TIMEOUT,
    BSP_CAN_TX_ERR_BUS,
} bsp_can_tx_status_t;

/**
  * @brief  启动 CubeMX 已初始化好的 CAN1
  * @retval BSP_CAN_TX_OK        成功
  * @retval BSP_CAN_TX_ERR_INIT  HAL_CAN_Start 失败
  * @retval BSP_CAN_TX_ERR_BUSY  已经启动
  *
  * @note   调用前必须已经执行 MX_CAN_Init()；
  *         本函数不重新配置位时间/引脚，避免和 CubeMX 重复初始化。
  */
bsp_can_tx_status_t bsp_can_tx_init(void);

/**
  * @brief  发送一帧标准数据帧，固定 8 字节
  * @param  std_id     11 位标准 ID（0x000..0x7FF）
  * @param  data       指向 8 字节数据
  * @param  timeout_ms 等待空闲邮箱/发送完成的总超时
  *                    - 0：只保证写入邮箱，不等待 ACK
  *                    - >0：等待发送完成；无 ACK/总线错误会超时
  * @retval BSP_CAN_TX_OK        成功
  * @retval BSP_CAN_TX_ERR_PARAM 参数非法
  * @retval BSP_CAN_TX_ERR_INIT  未初始化
  * @retval BSP_CAN_TX_ERR_BUSY  没有空闲邮箱且 timeout_ms=0
  * @retval BSP_CAN_TX_ERR_TIMEOUT 等邮箱/等完成超时
  * @retval BSP_CAN_TX_ERR_BUS   总线错误/bus-off
  */
bsp_can_tx_status_t bsp_can_tx_send(uint32_t std_id,
                                    const uint8_t data[BSP_CAN_TX_DATA_LEN],
                                    uint32_t timeout_ms);

/**
  * @brief  是否已经 HAL_CAN_Start
  */
uint8_t bsp_can_tx_is_ready(void);

#ifdef __cplusplus
}
#endif

#endif /* BSP_CAN_TX_H */
