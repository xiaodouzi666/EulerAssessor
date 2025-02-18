import _axios from 'axios';

const HOST = 'http://127.0.0.1:5000';

export enum Code {
  SUCCESS = 0,
  FAILED = 1,
  ERROR = -1,
}
// 使用别名
export type ResCode = Code;
export interface IResData {
  code: ResCode;
  data?: any;
  message: string;
  [string: string]: any;
}
export interface QueryParams {
  method: string;
  params?: {
    items: object;
  };
}
export interface IReq {
  url: string;
  method?: string;
  data?: any;
}
const baseURL = HOST;

const axios = _axios.create({
  baseURL: baseURL,
  timeout: 10000,
});

axios.interceptors.request.use(
  function (config) {
    config.headers['Content-Type'] = 'application/json';
    return config;
  },
  function (error) {
    return Promise.reject(error);
  }
);

axios.interceptors.response.use(
  function (response) {
    return response;
  },
  async function (error) {
    console.log('network error', error);
    if (error.code === 'ECONNABORTED') {
      console.error('请求超时');
    }
    return Promise.reject(error);
  }
);

/**
 * 发送HTTP请求的函数
 *
 * @param method
 * @param params 请求参数
 * @returns 返回请求结果的Promise对象
 */
export const request = async ({
  url,
  method,
  params,
}: any): Promise<IResData> => {
  const config: any = {
    url,
    method,
  };
  if (params) {
    if (method.toLocaleLowerCase() === 'post') {
      config.data = params;
    } else {
      config.params = params;
    }
  }

  try {
    const res = await axios({
      ...config,
    });
    return res.data;
  } catch (error) {
    console.log('error', error);
    return {
      code: -1,
      data: null,
      message: '请求失败',
    };
  }
};
