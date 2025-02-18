import React from 'react';
import { Space, Table, Tag } from 'antd';
import type { TableProps } from 'antd';

import { mockDiffDataApi } from '@/api';

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
    title: 'Version',
    dataIndex: 'version',
    key: 'version',
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
    dataIndex: 'action',
    key: 'action',
  },
  // {
  //   title: 'Action',
  //   key: 'action',
  //   render: (_, record) => (
  //     <Space size="middle">
  //       <a>Invite {record.name}</a>
  //       <a>Delete</a>
  //     </Space>
  //   ),
  // },
];

// const data: DataType[] = [
//   {
//     key: '1',
//     name: 'John Brown',
//     age: 32,
//     address: 'New York No. 1 Lake Park',
//     tags: ['nice', 'developer'],
//   },
//   {
//     key: '2',
//     name: 'Jim Green',
//     age: 42,
//     address: 'London No. 1 Lake Park',
//     tags: ['loser'],
//   },
//   {
//     key: '3',
//     name: 'Joe Black',
//     age: 32,
//     address: 'Sydney No. 1 Lake Park',
//     tags: ['cool', 'teacher'],
//   },
// ];

// const comparaApi = async () => {
//   const res = await PackageCompareApi();
//   console.log('compare', res);
//   diffApi();
// };

const Page: React.FC = () => {
  const [data, setData] = React.useState([]);

  const api = async () => {
    const res = await mockDiffDataApi();
    console.log('mockDiffDataApi', res);
    if (res?.packages_table) {
      setData(res.packages_table);
    }
  };

  React.useEffect(() => {
    api();
  }, []);
  return (
    <Table<DataType>
      columns={columns}
      dataSource={data}
      pagination={{ position: ['bottomCenter'] }}
      sticky={{ offsetHeader: 0 }}
      scroll={{ x: 'max-content', y: 55 * 8 }}
    />
  );
};

export default Page;
