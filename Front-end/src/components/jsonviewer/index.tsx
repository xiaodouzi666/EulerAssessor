import React, { Component } from 'react';

import JSONViewer from 'react-json-viewer';

export default function JsonViewer(props: any) {
  return <JSONViewer json={props.json} />;
}
