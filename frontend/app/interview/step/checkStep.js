'use client';

import { Box, Flex, Button } from '@chakra-ui/react';
import WebcamComponent from '../components/webcam';
import StepComponent from '../components/stepComponent';
import 'regenerator-runtime/runtime';
import React, { useState, useEffect } from 'react';

const CheckStep = ({ setCurrentStep }) => {
  const [permissionsGranted, setPermissionsGranted] = useState(false);

  const checkPermissions = async () => {
    try {
      await navigator.mediaDevices.getUserMedia({ audio: true, video: true });
      setPermissionsGranted(true);
    } catch (error) {
      console.error('권한 요청 실패:', error);
      setPermissionsGranted(false);
    }
  };

  const nextStep = () => {
    if (permissionsGranted) {
      setCurrentStep((prevSteps) => prevSteps + 1);
    }
  };

  // 권한 상태가 변경될 때마다 버튼의 활성화 상태를 업데이트
  useEffect(() => {
    const updateButtonState = () => {
      if (permissionsGranted) {
        console.log('권한이 허용되었습니다.');
      } else {
        console.log('권한이 필요합니다.');
      }
    };

    updateButtonState();
  }, [permissionsGranted]);

  return (
    <Box>
      <Flex justify={'space-around'} mb={'20px'}>
        <Box>
          <WebcamComponent />
          <Box
            background={'#DFE2FB'}
            h={'100px'}
            minW={'100%'}
            mt={'30px'}
          ></Box>
        </Box>
        <Box>
          <StepComponent
            checkPermissions={checkPermissions}
            permissionsGranted={permissionsGranted}
          />
          <Button
            w={'100%'}
            h={'100px'}
            background={'#DFE2FB'}
            fontFamily={'inter'}
            mt={'30px'}
            onClick={nextStep}
            isDisabled={!permissionsGranted} // 권한이 없으면 비활성화
          >
            {permissionsGranted ? '다음으로' : '권한 허용 필요'}
          </Button>
        </Box>
      </Flex>
    </Box>
  );
};

export default CheckStep;
