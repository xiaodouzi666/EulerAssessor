import * as forge from 'node-forge'
import { SIMAGIC_PUBLIC_KEY } from '@/constants'

interface PresetListItem {
  presetName?: string,
  [key: string]: any
}
type ValidatePresetName  = (name:string, presetList: PresetListItem[]) => boolean
export const isPresetNameExist:ValidatePresetName = (name, presetList = []) => {
  console.log(presetList)
  const sourceNames: string[] = presetList.map(item => item.presetName)
  return sourceNames.includes(name)
}

export const encryptData = (text: string) => {
  try {
    const publicKeyObj = forge.pki.publicKeyFromPem(SIMAGIC_PUBLIC_KEY);
    const encrypted = publicKeyObj.encrypt(text, 'RSA-OAEP', {
      md: forge.md.sha256.create(),
    });
    return forge.util.encode64(encrypted)
  } catch (error) {
    console.error('Encryption Error:', error); // 更详细的错误信息
    return '';
  }
};
