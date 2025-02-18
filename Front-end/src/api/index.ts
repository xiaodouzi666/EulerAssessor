import { request } from './request';

export const mockDiffDataApi = () => {
  return request({
    url: '/api/mock_diff_data',
    method: 'get',
  });
};
// 迁移
export const MigrationApi = () => {
  return request({
    url: '/api/migration_assessment',
    method: 'get',
  });
};

// 环境兼容信息收集
export const SourceCollectionApi = () => {
  return request({
    url: '/api/collect/source',
    method: 'post',
  });
};

export const TargetCollectionApi = () => {
  return request({
    url: '/api/collect/target',
    method: 'post',
  });
};

// 软件包分析
export const PackageCompareApi = () => {
  return request({
    url: '/api/packages/compare',
    method: 'post',
  });
};

export const PackageDiffApi = () => {
  return request({
    url: '/api/packages/differences',
    method: 'get',
  });
};

// 配置文件对比
// 硬件兼容/驱动对比
// 命令可用性对比
export const ConfigCompareApi = () => {
  return request({
    url: '/api/compare',
    method: 'post',
  });
};

export const ConfigDiffApi = () => {
  return request({
    url: '/api/diffresult',
    method: 'get',
  });
};
