import { Box, Text, Flex, Image, VStack } from '@chakra-ui/react';
const Section = () => {
  return (
    <Box mx={'100px'} pb={'100px'}>
      <Flex alignItems={'center'}>
        <Text fontSize={'xxx-large'} fontWeight={'800'} color={'#0066FF'}>
          Unail,IT &nbsp;
        </Text>{' '}
        <Text fontSize={'xxx-large'} fontWeight={'700'}>
          은
        </Text>
      </Flex>
      <Text fontSize={'xxx-large'} fontWeight={'700'}>
        맞춤형 AI 모의 면접을
      </Text>
      <Text fontSize={'xxx-large'} fontWeight={'700'}>
        제공합니다
      </Text>
      <Box mt={'30px'} w={'80%'} m={'30px auto 0 auto'}>
        <Image src="/about_section.png"></Image>
      </Box>
      <VStack fontSize={'xx-large'} fontWeight={'700'} gap={'20px'} mt={'30px'}>
        <Text>
          취준생에게는 이력서를 기반으로&nbsp;
          <Box as="span" color={'#0066FF'}>
            맞춤형 질문
          </Box>
          을 제공하고,
        </Text>
        <Text>
          기업은 회사 내부 데이터를 활용하여&nbsp;
          <Box as="span" color={'#0066FF'}>
            면접시스템을 커스터마이징
          </Box>
          할 수 있습니다
        </Text>
        <Text>
          각 면접에 대한&nbsp;
          <Box as="span" color={'#0066FF'}>
            세부적인 피드백
          </Box>
          을 평가 결과로 제공합니다
        </Text>
      </VStack>
    </Box>
  );
};

export default Section;
