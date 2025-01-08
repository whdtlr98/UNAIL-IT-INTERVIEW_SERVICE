'use client';

import { Box } from '@chakra-ui/react';
import Header from '../common/components/header';
import 'regenerator-runtime/runtime';
import React, { useState } from 'react';
import StepProgress from '../common/components/progress';
import UploadStep from './step/uploadStep';
import Container from '../common/components/container';
import CheckStep from './step/checkStep';
import InterviewStep from './step/interviewStep';
import UserGuard from '../common/utils/userGuard';

const StepRenderer = React.memo(({ steps, setCurrentStep }) => {
  switch (steps) {
    case 1:
      return <CheckStep setCurrentStep={setCurrentStep} />;
    case 2:
      return <UploadStep setCurrentStep={setCurrentStep} />;
    case 3:
      return <InterviewStep />;
    default:
      return null;
  }
});

function InterviewPage() {
  const [steps, setSteps] = useState([1, 2, 3]);
  const [currentStep, setCurrentStep] = useState(1);

  return (
    <UserGuard>
    <Box>
      <Container>
        <Header />
        <StepProgress steps={steps} currentStep={currentStep} />
        <StepRenderer steps={currentStep} setCurrentStep={setCurrentStep} />
      </Container>
    </Box>
    </UserGuard>
  );
}

export default InterviewPage;
