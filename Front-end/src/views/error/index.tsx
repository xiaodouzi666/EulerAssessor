import { useRouteError, useNavigate } from 'react-router-dom';
import {
  Button,
  Dialog,
  DialogSurface,
  DialogBody,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@fluentui/react-components';
import { useTranslation } from 'react-i18next';
const ErrorPage: React.FC = () => {
  const error: any = useRouteError();
  const navigate = useNavigate();
  const { t, i18n } = useTranslation();
  return (
    <Dialog open={true}>
      <DialogSurface style={{ width: 500 }}>
        <DialogBody>
          <DialogTitle> {t('errorDialog.oops')}!</DialogTitle>
          <DialogContent>
            <div
              style={{
                textAlign: 'center',
                fontSize: '16px',
                marginTop: '12px',
              }}
            >
              {t(
                'errorDialog.theFollowingErrorOccurredClickTheBackButtonToReturnToTheMainMenu'
              )}
              :
            </div>
            <div
              style={{
                textAlign: 'center',
                fontSize: '16px',
                marginTop: '12px',
              }}
            >
              {error.statusText || error.message}
            </div>
          </DialogContent>
          <DialogActions>
            <Button style={{ marginTop: '12px' }} onClick={() => navigate(`/`)}>
              {t('errorDialog.back')}
            </Button>
          </DialogActions>
        </DialogBody>
      </DialogSurface>
    </Dialog>
  );
};

export default ErrorPage;
