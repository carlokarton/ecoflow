from typing import Any

from . import BaseDevice, const
from .. import EcoflowMQTTClient
from ..entities import BaseSensorEntity, BaseNumberEntity, BaseSwitchEntity, BaseSelectEntity
from ..number import MaxBatteryLevelEntity, MinBatteryLevelEntity
from ..select import DictSelectEntity
from ..sensor import OutWattsSensorEntity, InWattsSensorEntity, LevelSensorEntity, \
    RemainSensorEntity, MiscBinarySensorEntity
from ..switch import EnabledEntity

MODES = {
    "Auto": {"sta": 0, "ctrl_mode": 0},
    "Grid": {"sta": 0, "ctrl_mode": 1},
    "Battery": {"sta": 1, "ctrl_mode": 1},
    "Off": {"sta": 2, "ctrl_mode": 1}
}


class ModeDictSelectEntity(DictSelectEntity):

    def __init__(self, client: EcoflowMQTTClient, n: int):
        super().__init__(client, "loadCmdChCtrlInfos[%i]" % n, const.SHP_CIRCUIT_N_MODE % (n + 1), MODES,
                         lambda value: {"sta": value.sta, "ctrlMode": value.ctrl_mode, "ch": 0, "cmdSet": 11, "id": 16})

    def _update_value(self, val: Any) -> bool:
        return super()._update_value({"sta": val.sta, "ctrl_mode": val.ctrlMode})


class SmartHomePanel(BaseDevice):

    def sensors(self, client: EcoflowMQTTClient) -> list[BaseSensorEntity]:
        res = [
            LevelSensorEntity(client, "energyInfos[0].batteryPercentage", const.SHP_AC_N_BATTERY_LEVEL % 1),
            OutWattsSensorEntity(client, "energyInfos[0].outputPower", const.SHP_AC_N_OUT_POWER % 1),
            InWattsSensorEntity(client, "energyInfos[0].lcdInputWatts", const.SHP_AC_N_IN_POWER % 1),
            RemainSensorEntity(client, "energyInfos[0].chargeTime", const.SHP_AC_N_CHARGE_TIME % 1),
            RemainSensorEntity(client, "energyInfos[0].dischargeTime", const.SHP_AC_N_DISCHARGE_TIME % 1),
            MiscBinarySensorEntity(client, "energyInfos[0].stateBean.isConnect", const.SHP_AC_N_CONNECTED % 1),
            MiscBinarySensorEntity(client, "energyInfos[0].stateBean.isEnable", const.SHP_AC_N_ENABLED % 1),

            LevelSensorEntity(client, "energyInfos[1].batteryPercentage", const.SHP_AC_N_BATTERY_LEVEL % 2),
            OutWattsSensorEntity(client, "energyInfos[1].outputPower", const.SHP_AC_N_OUT_POWER % 2),
            InWattsSensorEntity(client, "energyInfos[1].lcdInputWatts", const.SHP_AC_N_IN_POWER % 2),
            RemainSensorEntity(client, "energyInfos[1].chargeTime", const.SHP_AC_N_CHARGE_TIME % 2),
            RemainSensorEntity(client, "energyInfos[1].dischargeTime", const.SHP_AC_N_DISCHARGE_TIME % 2),
            MiscBinarySensorEntity(client, "energyInfos[1].stateBean.isConnect", const.SHP_AC_N_CONNECTED % 2),
            MiscBinarySensorEntity(client, "energyInfos[1].stateBean.isEnable", const.SHP_AC_N_ENABLED % 2),

        ]

        return res

    def numbers(self, client: EcoflowMQTTClient) -> list[BaseNumberEntity]:
        return [
            MaxBatteryLevelEntity(client, "forceChargeHigh", const.MAX_CHARGE_LEVEL, 50, 100,
                                  lambda value, params: {"moduleType": 0, "operateType": "TCP",
                                                         "params": {"discLower": int(params.get("discLower", 0)),
                                                                    "forceChargeHigh": value,
                                                                    "cmdSet": 11, "id": 29}}),

            MinBatteryLevelEntity(client, "discLower", const.MAX_CHARGE_LEVEL, 0, 30,
                                  lambda value, params: {"moduleType": 0, "operateType": "TCP",
                                                         "params": {"discLower": value,
                                                                    "forceChargeHigh": int(
                                                                        params.get("forceChargeHigh", 100)),
                                                                    "cmdSet": 11, "id": 29}})

        ]

    def switches(self, client: EcoflowMQTTClient) -> list[BaseSwitchEntity]:
        return [
            EnabledEntity(client, "energyInfos[0].stateBean.isGridCharge", const.SHP_AC_N_CHARGING % 1,
                          lambda value: {"moduleType": 0, "operateType": "TCP",
                                         "params": {"sta": value * 2, "ctrlMode": value, "ch": 10, "cmdSet": 11,
                                                    "id": 17}}),

            EnabledEntity(client, "energyInfos[1].stateBean.isGridCharge", const.SHP_AC_N_CHARGING % 1,
                          lambda value: {"moduleType": 0, "operateType": "TCP",
                                         "params": {"sta": value * 2, "ctrlMode": value, "ch": 10, "cmdSet": 11,
                                                    "id": 17}})

        ]

    def selects(self, client: EcoflowMQTTClient) -> list[BaseSelectEntity]:
        res = []
        res.extend(self.generate_mode_selects(client))

        return res

    def generate_sensors(self, client: EcoflowMQTTClient) -> list[BaseSensorEntity]:
        res = []
        for i in range(0, 11):
            res.append(InWattsSensorEntity(client, "infoList[%i].chWatt" % i, const.SHP_CIRCUIT_N_POWER % (i + 1)))
            res.append(MiscBinarySensorEntity(client, "loadCmdChCtrlInfos[%i].ctrlMode" % i,
                                              const.SHP_CIRCUIT_N_AUTO % (i + 1)))
        return res

    def generate_mode_selects(self, client: EcoflowMQTTClient) -> list[DictSelectEntity]:
        res = []
        for i in range(0, 10):
            res.append(ModeDictSelectEntity(client, i))
        return res
