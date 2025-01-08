import React from 'react';
import { Stack, HStack, Circle, Text, Box } from '@chakra-ui/react';

const StepProgress = ({ steps, currentStep }) => {
  return (
    <Stack m={'20px 0 40px 0'}>
      <HStack
        spacing={0}
        justify="center"
        position="relative"
        alignItems="center"
      >
        {steps.map((step, index) => (
          <React.Fragment key={index}>
            {index > 0 && (
              <Box
                w="200px"
                h="20px"
                bg={'#DFE2FB'}
                position="relative"
                zIndex={1}
              />
            )}
            <Circle
              size="70px"
              bg={index < currentStep ? '#0066FF' : '#DFE2FB'}
              color={'white'}
              position="relative"
              zIndex={2}
              p={2}
            >
              <Text fontSize="small" textAlign={'center'} fontWeight="bold" whiteSpace={'nowrap'}>
                {(() => {
                  switch (index) {
                    case 0:
                      return '환경 점검';
                    case 1:
                      return '정보 입력';
                    default:
                      return '면접 시작';
                  }
                })()}
              </Text>
            </Circle>
          </React.Fragment>
        ))}
      </HStack>
    </Stack>
  );
};

export default StepProgress;
