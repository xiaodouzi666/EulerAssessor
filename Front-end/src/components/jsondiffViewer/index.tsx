import ReactDiffViewer from 'react-diff-viewer-continued';
import React from 'react';
import ReactJsonViewCompare from 'react-json-view-compare';

export default function JsonDiffViewer({
  oldJson,
  newJson,
  ...restProps
}: any) {
  return (
    <ReactDiffViewer
      oldValue={JSON.stringify(oldJson, null, 2)}
      newValue={JSON.stringify(newJson, null, 2)}
      splitView={restProps.splitView || false}
      useDarkTheme={true}

      // useDarkTheme={true}
    />
  );
}

const oldData = {
  name: 'super',
  age: 18,
  task: [
    { name: 'eat', time: '09:00' },
    { name: 'work', time: '10:00' },
    { name: 'sleep', time: '22:00', a: [{ a: 1 }, 2] },
  ],
};
const newData = {
  name: 'coolapt',
  age: 20,
  task: [
    { name: 'eat', time: '09:00' },
    { name: 'work', time: '10:00' },
    { name: 'sleep', time: '23:00', a: [{ a: 2 }, 2] },
    { name: 'running', time: '08:00', a: {} },
  ],
};
export function JsonViewCompare() {
  return (
    <div className="App">
      <ReactJsonViewCompare oldData={oldData} newData={newData} />
    </div>
  );
}
