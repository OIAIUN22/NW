/**
  ******************************************************************************
  * @file    bsp_sg90.c
  * @brief   SG90 舵机 PWM 驱动实现
  *
  * 使用 TIM2：
  *   PSC  = TIM2_CLK / 1MHz - 1
  *   ARR  = 20000 - 1  -> 50Hz
  *   CCR  = 500..2500 -> 0.5..2.5ms
  *
  * 当前 NW 工程 HSI 8MHz、APB1 不分频：
  *   TIM2_CLK = 8MHz
  *   PSC = 7，计数频率 1MHz，50Hz 周期 20ms
  ******************************************************************************
  */

#include "pwm/bsp_sg90.h"

#include "stm32f1xx_hal.h"

static TIM_HandleTypeDef g_htim2;
static uint8_t g_ready = 0u;

static uint32_t bsp_sg90_hal_channel(bsp_sg90_channel_t ch)
{
    return (ch == BSP_SG90_CH2) ? TIM_CHANNEL_2 : TIM_CHANNEL_1;
}

static uint8_t bsp_sg90_channel_valid(bsp_sg90_channel_t ch)
{
    return (ch == BSP_SG90_CH1 || ch == BSP_SG90_CH2) ? 1u : 0u;
}

bsp_sg90_status_t bsp_sg90_init(void)
{
    if (g_ready != 0u) {
        return BSP_SG90_ERR_BUSY;
    }

    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_TIM2_CLK_ENABLE();

    GPIO_InitTypeDef gpio = {0};
    gpio.Pin = GPIO_PIN_0 | GPIO_PIN_1;
    gpio.Mode = GPIO_MODE_AF_PP;
    gpio.Pull = GPIO_NOPULL;
    gpio.Speed = GPIO_SPEED_FREQ_HIGH;
    HAL_GPIO_Init(GPIOA, &gpio);

    /*
     * F1 的定时器时钟：APB1 不分频时等于 PCLK1，否则为 PCLK1 的 2 倍。
     * 这里按当前 RCC 配置动态计算，避免以后改时钟后 50Hz 变掉。
     */
    uint32_t tim_clk = HAL_RCC_GetPCLK1Freq();
    if ((RCC->CFGR & RCC_CFGR_PPRE1) != RCC_CFGR_PPRE1_DIV1) {
        tim_clk *= 2u;
    }
    if (tim_clk < 1000000u || (tim_clk % 1000000u) != 0u) {
        return BSP_SG90_ERR_INIT;
    }

    const uint32_t psc = (tim_clk / 1000000u) - 1u;
    if (psc > 0xFFFFu) {
        return BSP_SG90_ERR_INIT;
    }

    g_htim2.Instance = TIM2;
    g_htim2.Init.Prescaler = psc;
    g_htim2.Init.CounterMode = TIM_COUNTERMODE_UP;
    g_htim2.Init.Period = 20000u - 1u; /* 1MHz / 20000 = 50Hz */
    g_htim2.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
    g_htim2.Init.RepetitionCounter = 0;
    g_htim2.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_ENABLE;

    if (HAL_TIM_PWM_Init(&g_htim2) != HAL_OK) {
        return BSP_SG90_ERR_INIT;
    }

    TIM_OC_InitTypeDef oc = {0};
    oc.OCMode = TIM_OCMODE_PWM1;
    oc.Pulse = BSP_SG90_CENTER_US;
    oc.OCPolarity = TIM_OCPOLARITY_HIGH;
    oc.OCFastMode = TIM_OCFAST_DISABLE;

    if (HAL_TIM_PWM_ConfigChannel(&g_htim2, &oc, TIM_CHANNEL_1) != HAL_OK) {
        return BSP_SG90_ERR_INIT;
    }
    if (HAL_TIM_PWM_ConfigChannel(&g_htim2, &oc, TIM_CHANNEL_2) != HAL_OK) {
        return BSP_SG90_ERR_INIT;
    }

    if (HAL_TIM_PWM_Start(&g_htim2, TIM_CHANNEL_1) != HAL_OK) {
        return BSP_SG90_ERR_INIT;
    }
    if (HAL_TIM_PWM_Start(&g_htim2, TIM_CHANNEL_2) != HAL_OK) {
        (void)HAL_TIM_PWM_Stop(&g_htim2, TIM_CHANNEL_1);
        return BSP_SG90_ERR_INIT;
    }

    g_ready = 1u;
    return BSP_SG90_OK;
}

bsp_sg90_status_t bsp_sg90_set_pulse_us(bsp_sg90_channel_t ch,
                                        uint16_t us)
{
    if (g_ready == 0u) {
        return BSP_SG90_ERR_STATE;
    }
    if (bsp_sg90_channel_valid(ch) == 0u) {
        return BSP_SG90_ERR_PARAM;
    }
    if (us < BSP_SG90_MIN_PULSE_US || us > BSP_SG90_MAX_PULSE_US) {
        return BSP_SG90_ERR_PARAM;
    }

    __HAL_TIM_SET_COMPARE(&g_htim2, bsp_sg90_hal_channel(ch), us);
    return BSP_SG90_OK;
}

bsp_sg90_status_t bsp_sg90_disable(bsp_sg90_channel_t ch)
{
    if (g_ready == 0u) {
        return BSP_SG90_ERR_STATE;
    }
    if (bsp_sg90_channel_valid(ch) == 0u) {
        return BSP_SG90_ERR_PARAM;
    }

    (void)HAL_TIM_PWM_Stop(&g_htim2, bsp_sg90_hal_channel(ch));
    return BSP_SG90_OK;
}

uint8_t bsp_sg90_is_ready(void)
{
    return g_ready;
}
