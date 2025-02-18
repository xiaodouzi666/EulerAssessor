export * from './validate'
const MAX_WHEEL_ANGLE = 900
import { CURRENT_BASE_PRESET_KEY } from '@/constants'
export const formatPedalFeedbackOption = (option) => {
    return {
        trigger: 0,
        isOn: false,
        force_on: false,
        amplitude: 12,
        frequency: 50,
        ...option
    }
}

export const sortPresetByAlphabetically = (list) => {
    const newPresets = [...list];
    newPresets.sort((a, b) => {
      const presetNameA = a.presetName.toUpperCase();
      const presetNameB = b.presetName.toUpperCase();

      if (presetNameA < presetNameB) {
        return -1;
      }
      if (presetNameA > presetNameB) {
        return 1;
      }
      return 0;
    });

    return newPresets;
  };

export const genConicGradient = (colors: Array<string>) => {
  if(!colors) return
  const num = colors.length;
  const percent = +(100 / num).toFixed(2)

  let bgColor = '';

  [...colors, colors[0]].forEach((color, index) => {
    bgColor += `,${color} ${Math.ceil(+(percent * index).toFixed(2))}%`
  })

  return `conic-gradient(from var(--wheel-angle), ${bgColor.slice(1)})`
}

export const breathSpeed = (prev) => {
  return Math.abs(160 - (((prev + 1) / 160) % 2) * 160)
}

export const mergeArrays = (array1: any[], array2: any[]): any[] => {
  // 将第一个数组转换为对象，以 key 为键
  const map = new Map(array1.map(item => [item.key, item]));

  // 遍历第二个数组，只处理与第一个数组中 key 相同的对象
  array2.forEach(item => {
    if (map.has(item.key)) {
      // 如果 map 中已经存在该 key，合并对象
      const existingItem = map.get(item.key);
      for (const key in item) {
        if (existingItem[key] === undefined || existingItem[key] === '') {
          existingItem[key] = item[key];
        }
      }
    }
  });

  // 将 map 转换回数组
  return Array.from(map.values());
}

export const getMaxWheelAngle = (maxWheelAngle?: number): number => {
  return maxWheelAngle ?? (JSON.parse(
    window.storageHandler.getValue(CURRENT_BASE_PRESET_KEY)
  )?.presetInfo?.max_wheel_angle ?? MAX_WHEEL_ANGLE);
}

export const formatWheelAngle = (wheel_angle: number = 0, maxWheelAngle?: number) => {
  const _maxWheelAngle = getMaxWheelAngle(maxWheelAngle);
  return Math.floor(
    (wheel_angle / 65535) * _maxWheelAngle - _maxWheelAngle / 2
  );
}
