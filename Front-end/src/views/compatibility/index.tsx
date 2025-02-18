import React, { useState, useEffect } from 'react';
import { Space, Table, Tag } from 'antd';
import type { TableProps } from 'antd';
import { CheckOutlined, CloseOutlined } from '@ant-design/icons';
import { mockDiffDataApi } from '@/api';

interface DataType {
  key?: string;
  name: string;
  newVer: boolean;
  oldVer: boolean;
  age?: number;
  address?: string;
  tags?: string[];
}

const columns: TableProps<DataType>['columns'] = [
  {
    title: '动态接口名称',
    dataIndex: 'label',
    key: 'label',
    render: (text) => <a>{text}</a>,
  },

  {
    title: '新版本',
    key: 'newVer',
    dataIndex: 'newVer',
    width: '200px',
    render: (_, record) => (
      <>{record.newVer ? <CheckOutlined /> : <CloseOutlined />}</>
    ),
  },
  {
    title: '旧版本',
    key: 'oldVer',
    width: '200px',
    render: (_, record) => (
      <>{record.oldVer ? <CheckOutlined /> : <CloseOutlined />}</>
    ),
  },
];

const list = [
  { name: '动态库接口1', oldValue: true, newValue: true },
  { name: '动态库接口2', oldValue: false, newValue: true },
  { name: '动态库接口3', oldValue: true, newValue: true },
  { name: '动态库接口4', oldValue: false, newValue: true },
  { name: '动态库接口5', oldValue: true, newValue: false },
  { name: '动态库接口6', oldValue: true, newValue: true },
  { name: '动态库接口7', oldValue: true, newValue: false },
  { name: '动态库接口8', oldValue: false, newValue: true },
  { name: '动态库接口9', oldValue: true, newValue: false },
  { name: '动态库接口10', oldValue: true, newValue: true },
  { name: '动态库接口11', oldValue: false, newValue: true },
  { name: '动态库接口12', oldValue: true, newValue: false },
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
];

const Page: React.FC = () => {
  const [data, setData] = useState([]);
  const api = async () => {
    const res = await mockDiffDataApi();
    console.log('mockDiffDataApi', res);
    if (res?.compatibility) {
      setData(res.compatibility);
    }
  };

  useEffect(() => {
    api();
  }, []);
  return (
    <div
      style={{
        position: 'relative',
        height: '100%',
        overflowY: 'scroll',
      }}
    >
      <Table<DataType>
        bordered
        columns={columns}
        dataSource={data}
        pagination={{ position: ['bottomCenter'] }}
        sticky={{ offsetHeader: 0 }}
        scroll={{ x: 'max-content', y: 55 * 8 }}
      />
    </div>
  );
};

export default Page;
