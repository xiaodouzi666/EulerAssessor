import React, { useState } from 'react';
import { Space, Table, Tag, Col, Row } from 'antd';
import type { TableProps } from 'antd';

import { SourceCollectionApi, TargetCollectionApi } from '@/api';

interface DataType {
  key: string;
  name: string;
  age: number;
  address: string;
  tags: string[];
}

const columns: TableProps<DataType>['columns'] = [
  {
    title: 'Name',
    dataIndex: 'name',
    key: 'name',
    render: (text) => <a>{text}</a>,
  },
  {
    title: 'Age',
    dataIndex: 'age',
    key: 'age',
  },
  {
    title: 'Address',
    dataIndex: 'address',
    key: 'address',
  },
  {
    title: 'Tags',
    key: 'tags',
    dataIndex: 'tags',
    render: (_, { tags }) => (
      <>
        {tags.map((tag) => {
          let color = tag.length > 5 ? 'geekblue' : 'green';
          if (tag === 'loser') {
            color = 'volcano';
          }
          return (
            <Tag color={color} key={tag}>
              {tag.toUpperCase()}
            </Tag>
          );
        })}
      </>
    ),
  },
  {
    title: 'Action',
    key: 'action',
    render: (_, record) => (
      <Space size="middle">
        <a>Invite {record.name}</a>
        <a>Delete</a>
      </Space>
    ),
  },
];

const data: DataType[] = [
  {
    key: '1',
    name: 'John Brown',
    age: 32,
    address: 'New York No. 1 Lake Park',
    tags: ['nice', 'developer'],
  },
  {
    key: '2',
    name: 'Jim Green',
    age: 42,
    address: 'London No. 1 Lake Park',
    tags: ['loser'],
  },
  {
    key: '3',
    name: 'Joe Black',
    age: 32,
    address: 'Sydney No. 1 Lake Park',
    tags: ['cool', 'teacher'],
  },
  {
    key: '4',
    name: 'John Brown',
    age: 32,
    address: 'New York No. 1 Lake Park',
    tags: ['nice', 'developer'],
  },
  {
    key: '5',
    name: 'Jim Green',
    age: 42,
    address: 'London No. 1 Lake Park',
    tags: ['loser'],
  },
  {
    key: '6',
    name: 'Joe Black',
    age: 32,
    address: 'Sydney No. 1 Lake Park',
    tags: ['cool', 'teacher'],
  },
  {
    key: '7',
    name: 'John Brown',
    age: 32,
    address: 'New York No. 1 Lake Park',
    tags: ['nice', 'developer'],
  },
  {
    key: '8',
    name: 'Jim Green',
    age: 42,
    address: 'London No. 1 Lake Park',
    tags: ['loser'],
  },
  {
    key: '9',
    name: 'Joe Black',
    age: 32,
    address: 'Sydney No. 1 Lake Park',
    tags: ['cool', 'teacher'],
  },
];

// const infos = [
//   { label: '系统版本', value: 'os_info.release' },
//   { label: '内核', value: 'os_info.version' },
//   { label: '空间', value: 'disk_info' },
//   { label: '板卡', value: 'hardware_info.pci_devices' },
//   { label: '挂载', value: '' },
//   { label: '设备驱动', value: 'hardware_info.kernel_modules' },
//   { label: '网络状态', value: 'network_info' },
//   { label: '端口', value: 'network_info' },
//   { label: '系统配置参数', value: '' },
//   { label: '环境变量', value: 'environment_variables' },
//   { label: '进程', value: 'processes' },
//   { label: '服务状态', value: 'services_info' },
// ];
const infos = [
  { label: '系统版本', value: 'os_info.release' },
  { label: '内核', value: 'os_info.version' },
  { label: '空间', value: 'disk_info' },
  { label: '板卡', value: 'hardware_info.pci_devices' },
  { label: '挂载', value: 'disk_info' },
  { label: '设备驱动', value: 'hardware_info.kernel_modules' }, // 目标可用 kernel_modules
  { label: '网络状态', value: 'network_info' },
  { label: '端口', value: 'network_info' },
  { label: '系统配置参数', value: 'config_files' }, // 需要额外过滤 /etc/sysctl.conf，前端试试嫩不能处理，不行就我来
  { label: '环境变量', value: 'environment_variables' },
  { label: '进程', value: 'processes' },
  { label: '服务状态', value: 'services_info' },
];

const Group: React.FC = () => {
  const [data, setData] = useState({});
  const sourceApi = async () => {
    const res = await SourceCollectionApi();
    console.log('res', res);
    targetApi();
  };

  const targetApi = async () => {
    const res = await TargetCollectionApi();
    console.log('target res', res);
    if (res.data) {
      setData(res.data);
    }
  };
  React.useEffect(() => {
    sourceApi();
  }, []);

  React.useEffect(() => {
    console.log('config_files', data['config_files']);
  }, [data]);

  return (
    <div
      style={{
        height: '100vh',
        overflowY: 'auto',
      }}
    >
      <div
        style={{
          marginTop: 20,
        }}
      >
        <Row gutter={[30, 30]}>
          {infos.map((info, index) => {
            return (
              <Col span={12} key={index}>
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    color: '#000',
                    fontSize: 16,
                  }}
                >
                  <p
                    style={{
                      textIndent: '20px',
                      whiteSpace: 'nowrap',
                      minWidth: '120px',
                      // textAlign: 'right',
                    }}
                  >
                    {info.label}
                  </p>
                  :
                  <p
                    style={{
                      whiteSpace: 'wrap',
                      fontSize: '14px',
                      wordBreak: 'break-all',
                      wordWrap: 'break-word',
                    }}
                    dangerouslySetInnerHTML={{
                      __html: info.value.includes('.')
                        ? JSON.stringify(
                            info.value
                              .split('.')
                              .reduce((prev, next) => prev?.[next], data)
                              ?.includes?.('\n')
                              ? info.value
                                  .split('.')
                                  .reduce((prev, next) => prev?.[next], data)
                                  ?.replace?.(/\n/g, '<br>')
                              : info.value
                                  .split('.')
                                  .reduce((prev, next) => prev?.[next], data)
                          )
                        : JSON.stringify(
                            data[info.value]?.includes?.('\n')
                              ? data[info.value]?.replace?.(/\n/g, '<br>')
                              : data[info.value]
                          ),
                    }}
                  >
                    {/* {info.value.includes('.')
                      ? JSON.stringify(
                          info.value
                            .split('.')
                            .reduce((prev, next) => prev?.[next], data)
                            ?.replace?.(/\n/g, '<br>')
                        )
                      : JSON.stringify(
                          data[info.value]?.replace?.(/\n/g, '<br>')
                        )} */}
                  </p>
                </div>
              </Col>
            );
          })}
        </Row>
      </div>
    </div>
  );
};

export default Group;

