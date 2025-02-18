import React, { useState, useEffect } from 'react';
import { Space, Table, Tag } from 'antd';
import type { TableProps } from 'antd';
import { JsonDiffViewer } from '@components';
import { MigrationApi } from '@/api';

const Page: React.FC = () => {
  const [data, setData] = useState<any>([]);
  const json = {
    name: 'Narendra',
    age: 32,
    place: {
      name: 'Delhi',
      pin: '110017',
    },
    likes: ['Apple', 'Banana', 'Mango'],
    test: {
      loginData: null,
    },
    todos: [
      {
        task: 'Write  Book',
        done: false,
      },
      {
        task: 'Learn  React',
        done: true,
      },
      {
        task: 'Buy  Mobile',
        done: false,
      },
    ],
    dateWiseData: {
      '2016-02-14': {
        availableRooms: 10,
        soldRooms: 20,
      },
      '2016-02-15': {
        availableRooms: 15,
        soldRooms: 15,
      },
      '2016-02-16': {
        availableRooms: 5,
        soldRooms: 25,
      },
      '2016-02-17': {
        availableRooms: 0,
        soldRooms: 30,
      },
    },
  };

  const api = async () => {
    const res = await MigrationApi();
    setData(res);
  };
  useEffect(() => {
    api();
  }, []);

  return (
    <div
      style={{
        position: 'relative',
        height: '100vh', // 让页面充满屏幕高度
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: '#2e303c',
      }}
    >
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
        }}
      >
        <div
          style={{
            display: 'inline-block',
            backgroundColor: '#2e303c',
            textAlign: 'left',
            lineHeight: '1.5',
            textIndent: '2em',
          }}
        >
          可行性评分： {data.score} / 100
        </div>
        <div
          style={{
            display: 'inline-block',
            backgroundColor: '#2e303c',
            textAlign: 'left',
            lineHeight: '1.5',
            textIndent: '2em',
          }}
        >
          {data.message}
        </div>
  
        <div
          style={{
            display: 'inline-block',
            backgroundColor: '#2e303c',
            textAlign: 'left',
            lineHeight: '1.5',
            textIndent: '2em',
            marginTop: '50px',
          }}
        >
          风险：
          <div
            style={{
              marginLeft: '40px',
            }}
          >
            {Array.isArray(data.risks)
              ? data.risks.map((item, index) => {
                  return (
                    <div key={index} style={{ marginTop: '20px' }}>
                      <div>id: {item.id}</div>
                      <div>title: {item.title}</div>
                      <div>description: {item.description}</div>
                    </div>
                  );
                })
              : JSON.stringify(data.risks)}
          </div>
        </div>
  
        <div
          style={{
            display: 'inline-block',
            backgroundColor: '#2e303c',
            textAlign: 'left',
            lineHeight: '1.5',
            textIndent: '2em',
            marginTop: '50px',
          }}
        >
          建议：
          <div
            style={{
              marginLeft: '40px',
            }}
          >
            {Array.isArray(data.suggestions)
              ? data.suggestions.map((item, index) => {
                  return <div key={index}>{item}</div>;
                })
              : JSON.stringify(data.suggestions)}
          </div>
        </div>
      </div>
    </div>
  );
  
};

export default Page;

