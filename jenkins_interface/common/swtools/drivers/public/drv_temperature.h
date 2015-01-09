/*************************************************************************************************
 * Icera Semiconductor
 * Copyright (c) 2006
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_temperature.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup TemperatureDriver  Temperature Measurement
 *
 */

/**
 * @addtogroup TemperatureDriver
 * @{
 */

/**
 * @file drv_temperature.h Temperature measurement driver public
 *       interface
 *
 */


#ifndef DRV_TEMPERATURE_H
#define DRV_TEMPERATURE_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/

/*************************************************************************************************
 * Macros
 ************************************************************************************************/
#define DRV_TEMP_INPUT_PRECISION_NA false

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/
/**
 * Abstraction type for drv_TemperatureSensor and drv_RfADCTempInput
 * @see drv_TemperatureSensor
 * @see drv_RfADCTempInput
 */
typedef unsigned char drv_TempSensorGeneric ;

/**
 * enumeration of the temperature sensors
 * @see drv_TemperatureSensors
 */
typedef enum
{
    DRV_TEMP_SENSOR_GSM   = 0,
    DRV_TEMP_SENSOR_WCDMA = 1,
    DRV_TEMP_SENSOR_TRINI = 2,
    DRV_TEMP_SENSOR_EXT   = 3,
    DRV_TEMP_SENSOR_AFC   = 4,
#if defined (TARGET_DXP9140)
    DRV_TEMP_SENSOR_INT0  = 5,
    DRV_TEMP_SENSOR_INT1  = 6,
#endif
    DRV_NUM_TEMP_SENSOR,
} drv_TemperatureSensor;

/**
 * enumeration of Temperature inputs of Auxilliary ADC
 */
typedef enum
{
    DRV_RF_ADC_TEMP_INP0  = 0,
    DRV_RF_ADC_TEMP_INP1  = 1,
    DRV_RF_ADC_TEMP_INP2  = 2,
    DRV_RF_ADC_TEMP_INP3  = 3,
    DRV_RF_ADC_TEMP_INP_NUM,
    DRV_RF_ADC_TEMP_INP_INVALID,

} drv_RfADCTempInput;

#if defined (TARGET_DXP9140)
/**
 * enumeration of Temperature inputs of internal temperature sensors
 */
typedef enum
{
    DRV_TEMP_SENSOR_INT_INP0 = DRV_RF_ADC_TEMP_INP_NUM,
    DRV_TEMP_SENSOR_INT_INP1,
    DRV_TEMP_SENSOR_INT_INP_NUM,
} drv_InternalTemperatureSensor;
#endif

/**
 * enumeration of Voltage inputs of Auxilliary ADC
 */
typedef enum
{
    DRV_RF_ADC_VOLT_INP0  = 0,
    DRV_RF_ADC_VOLT_INP1  = 1,
    DRV_RF_ADC_VOLT_INP2  = 2,
    DRV_RF_ADC_VOLT_INP3  = 3,
    DRV_RF_ADC_VOLT_INP_NUM,
    DRV_RF_ADC_VOLT_INP_INVALID,

} drv_RfADCVoltInput;

/**
 * Type of temperature reading
 */

typedef enum
{
    DRV_TEMP_READING_ADC          = 0,  // raw ADC value
    DRV_TEMP_READING_ADC_FILTERED,      // filtered raw ADC value
    DRV_TEMP_READING_TEMP,              // ADC value converted to temperature
    DRV_TEMP_READING_TEMP_FILTERED,     // filtered temperature
    DRV_TEMP_READING_NB,

} drv_TemperatureReading;


#define ADC_INVALID_VALUE -1

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/
/* Load temperature calibration data*/
extern bool drv_TempLoadCalData(void);

/**
 * Returns true if there is a new temperature reading
 * @return temperature
 */
extern bool drv_TemperatureCheckAfcTemp();

/**
 * Returns last temperature read into kalman filter
 * @return temperature
 */
extern int drv_TemperatureGetAfcTemp();

/**
 * Initialize temperature monitor
 *
 * @note This routine can be invoked from  DXP1 only
 *
 * @return none
 */
extern void drv_TemperatureInit(void);

/** 
 * Converts an ADC reading into a deci-Kelvin temperature value 
 * using the appropriate temperature curve from the cal table. 
 * 
 * @param  sensor  Sensor from which ADC reading has been read
 * @param  adc_val ADC reading to be converted
 * 
 * @return Temperature reading in deci-Kelvin (Kelvin*10)
 */
extern int32 drv_TemperatureConvert(drv_TempSensorGeneric sensor, int32 adc_val);

/**
 * Read temperature of a sensor.
 *
 * @note: For Factory test, the returned temperature is *not* after applying the HKADC calibration offset.
 *
 * @return temperature in units of "Kelvin*10"
 */
extern int drv_Temperature(drv_TemperatureSensor sensor);

/**
 * Read temperature at a particular temperature input
 *
 * @note: For Factory test, the returned temperature is *not* after applying the HKADC calibration offset.
 *        Voluntarily preventing link if ENH_DRV_TEMPERATURE undefined.
 *
 * @return value
 */
extern int drv_TemperatureAtInput(drv_RfADCTempInput adc);

/**
 * Read temperature of a particular tempeature sensor
 * @note: For Factory test, the returned temperature is *not* after applying the HKADC calibration offset.
 *        Voluntarily preventing link if ENH_DRV_TEMPERATURE undefined.
 *
 * @return value
 */
extern int drv_TempSensorReading(drv_TemperatureSensor  sensor,
                                 drv_TemperatureReading reading,
                                 bool                   with_cal);
/**
 * Read filtered/unfiltered values of temperature or Raw ADC value for a particular sensor.
 *
 * @param sensor  Sensor on which temperature is read.
 *                drv_TempSensorGeneric is an abtraction type. See the note section for details.
 * @param reading The type of temperature reading
 *
 * @return value
 *
 * @note For Factory test, the returned temperature is *not* after applying the HKADC calibration offset.
 * @note Use type drv_TemperatureSensor when using the Trini sensor.
 *       Use type drv_RfADCTempInput when using sensor plug on Auxilliary ADC (Enhanced temp mode)
 *
 * @see drv_TemperatureSensor
 * @see drv_RfADCTempInput
 */
extern int drv_TemperatureVal(drv_TempSensorGeneric sensor, drv_TemperatureReading reading);

/**
 * Read filtered/unfiltered values of temperature or Raw ADC value for a particular sensor.
 * There is an additional option to ask for values with or without HKADC calibration
 *
 * @param sensor          Sensor on which temperature is read.
 *                        drv_TempSensorGeneric is an abtraction type. See the note section for details.
 * @param reading         The type of temperature reading
 * @param lower_precision True if temperature obtained in lower precision (only applicable for Trini sensor)
 * @with_cal              True to use the calibration data
 *
 * @return                value
 *
 * @note Use type drv_TemperatureSensor when using the Trini sensor.
 *       Use type drv_RfADCTempInput when using sensor plug on Auxilliary ADC (Enhanced temp mode)
 *
 * @see  drv_TemperatureSensor
 * @see  drv_RfADCTempInput
 */
extern int32 drv_TempGetReading(drv_TempSensorGeneric sensor,
                                drv_TemperatureReading reading,
                                bool lower_precision,
                                bool with_cal);

/**
 * Make valid or unvalid a given thermistor
 *
 * @param sensor Sensor on which temperature is read.
 *                drv_TempSensorGeneric is an abtraction type. See the note section for details.
 * @param valid  Set true if thermistor is valid, false otherwise.
 *
 * @note  Use type drv_TemperatureSensor when using the Trini sensor.
 *        Use type drv_RfADCTempInput when using sensor plug on Auxilliary ADC (Enhanced temp mode)
 *
 * @see   drv_TemperatureSensor
 * @see   drv_RfADCTempInput
 *
 */
extern void drv_TemperatureSetSensorValid(drv_TempSensorGeneric sensor, bool valid);

/**
 * Tells if the current termistor is valid
 *
 * @param  sensor Sensor on which temperature is read.
 *                drv_TempSensorGeneric is an abtraction type. See the note section for details.
 *
 * @return true if enhanced mode supported, false otherwise.
 *
 * @note   Use type drv_TemperatureSensor when using the Trini sensor.
 *         Use type drv_RfADCTempInput when using sensor plug on Auxilliary ADC (Enhanced temp mode)
 *
 * @see    drv_TemperatureSensor
 * @see    drv_RfADCTempInput
 */
extern bool drv_TemperatureGetSensorValid(drv_TempSensorGeneric sensor);

/**
 * Inform if the Temperature driver supports the enhanced mode.
 *
 * @return true if enhanced mode supported, false otherwise.
 */
bool drv_TemperatureEnhancedModeSupport(void);

/**
 * Returns the maximum number of supported sensors.
 *
 * @return Max number of supported sensors.
 */
extern uint32 drv_TemperatureGetMaxSensorsNum(void);

/**
 * Returns the maximum number of logical sensors.
 *
 * @return Max number of logical sensors.
 */
extern uint32 drv_TemperatureGetMaxLogicalSensorsNum(void);

/**
 * Restores and restart internal temp-sensors.
 */
extern void drv_TemperatureRestore(void);

#endif

/** @} END OF FILE */
