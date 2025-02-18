export const buildSdbQueryBody = (...args: any[]) => {
  return `
      {
          "id": 1,
          "jsonrpc": "2.0",
          "method": "query",
          "params": {
              "items": [${args.join(',')}]
          }
      }`;
};

export const buildSdbGetConfigBody = (...args: any[]) => {
  return `
      {
          "id": 1,
          "jsonrpc": "2.0",
          "method": "get_config",
          "params": {
              "items": [${args.join(',')}]
          }
      }`;
};

export const buildSdbGetConfigDevice = (params) => {
  return JSON.stringify({
    id: 1,
    jsonrpc: '2.0',
    method: 'get_device_config_list',
    // "params": {
    //     "items": params
    // }
  });
};

export const buildSdbSetConfigBody = (body) => {
  return `
    {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "set_config",
        "params": {
            "items": ${JSON.stringify(body)}
        }
    }`;
};

export const buildSdbLoopTestBody = (body) => {
  return `
    {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "production_ret",
        "params": {
            "items": ${JSON.stringify(body)}
        }
    }`;
};

export const sdbCefQuery = async (method, params) => {
  const request = params ? `${method}:${JSON.stringify(params)}` : `${method}:`;
  return new Promise((resolve, reject) => {
    try {
      window.cefQuery({
        request,
        onSuccess: function (response) {
          console.log('sdbCefQuery--onSuccess: ', request, response);
          resolve(response);
        },
        onFailure: function (error_code, error_message) {
          console.log('sdbCefQuery--onFailure: ', request, {
            error_code,
            error_message,
          });
          reject({
            error_code,
            error_message,
          });
        },
      });
    } catch (error) {
      console.log('sdbCefQuery--catchError: ', request, error);
      reject({
        error,
      });
    }
  });
};
