import React, { useState } from 'react';
import { Space, Switch, Table, Tag } from 'antd';
import type { TableProps } from 'antd';
import { JsonViewer, JsonDiffViewer } from '@components';
import { mockDiffDataApi } from '@/api';

interface DataType {
  key: string;
  name: string;
  age: number;
  address: string;
  tags: string[];
}

const Page: React.FC = () => {
  const [splitView, setSplitView] = useState(true);
  const [newJson, setNewJson] = useState('');
  const [oldJson, setOldJson] = useState('');

  const api = async () => {
    const res = await mockDiffDataApi();
    console.log('mockDiffDataApi', res);
    if (res?.newJson) {
      setNewJson(res.newJson);
    }
    if (res?.oldJson) {
      setOldJson(res.oldJson);
    }
  };

  React.useEffect(() => {
    api();
  }, []);

  return (
    <div
      style={{
        position: 'relative',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
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
        {/* <Switch
          value={splitView}
          onChange={(checked) => setSplitView(checked)}
        ></Switch> */}
      </div>

      <div
        style={{
          flex: 1,
          overflowX: 'scroll',
          overflowY: 'scroll',
          backgroundColor: '#2e303c',
        }}
      >
        <JsonDiffViewer
          oldJson={oldJson}
          splitView={splitView}
          newJson={newJson}
        />
      </div>
    </div>
  );
};

export default Page;
