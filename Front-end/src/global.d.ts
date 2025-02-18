import {
  MainWindowHandler,
  UpdateHandler,
  SdbHandler,
  StorageHandler,
  GmHandler,
  DvmHandler,
  SimproMessageHandler
} from './preload';

interface CefQueryParams {
  request: string
  onSuccess: (response: any) => void
  onFailure: (code: number, msg: string) => void
}

declare global {
  function cefQuery(params: CefQueryParams): void;
  function _cefQuery(params): any;
  // eslint-disable-next-line no-unused-vars
  interface Window {
  	myCustomProperty: string;
    mainWindowHandler: MainWindowHandler;
    updateHandler: UpdateHandler;
    sdbHandler: SdbHandler;
    storageHandler: StorageHandler;
    gmHandler: GmHandler;
    dvmHandler: DvmHandler;
    simproMessageHandler: SimproMessageHandler
    cefQuery: (o: CefQueryParams) => void;
  }
}

export {};
