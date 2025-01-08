import React, { useMemo } from 'react';
import {
  Box,
  VStack,
  Heading,
  Text,
  Flex,
  Image,
  SimpleGrid,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
} from '@chakra-ui/react';
import { FaComment } from 'react-icons/fa';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { formatDate } from '@/app/common/utils/dayformat';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const DetailLog = ({ interviewLogList, reportData }) => {
  const evaluationResults = reportData ? JSON.parse(reportData.detail_feedback) : {};

  // 차트 데이터 생성
  const chartData = useMemo(() => {
    const labels = Object.keys(evaluationResults);
    const accuracyScores = labels.map(key => evaluationResults[key].정확성.score);
    const jobFitScores = labels.map(key => evaluationResults[key].직무적합성_역량.score);
    const logicScores = labels.map(key => evaluationResults[key].논리성.score);

    return {
      labels,
      datasets: [
        {
          label: '정확성',
          data: accuracyScores,
          backgroundColor: 'rgba(75, 192, 192, 0.6)',
          borderColor: 'rgba(75, 192, 192, 1)',
          borderWidth: 1,
        },
        {
          label: '직무적합성 및 역량',
          data: jobFitScores,
          backgroundColor: 'rgba(255, 99, 132, 0.6)',
          borderColor: 'rgba(255, 99, 132, 1)',
          borderWidth: 1,
        },
        {
          label: '논리성',
          data: logicScores,
          backgroundColor: 'rgba(54, 162, 235, 0.6)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 1,
        },
      ],
    };
  }, [evaluationResults]);

  return (
    <Box maxWidth="900px" margin="auto" p={5}>
      <Box borderBottom="4px solid black" pb="10px" w="100%">
        <Text fontSize={['24px', '26px', '30px']} fontWeight="bold">
          면접 세부 내용
        </Text>
      </Box>

      {/* Log Section */}
      <VStack spacing={6} align="stretch" mt={8}>
        <Flex justifyContent="space-between" alignItems="center">
          <Heading as="h2" size="md" mb={2}>
            면접 로그
          </Heading>
          <Box>
          </Box>
        </Flex>

        {interviewLogList.map((item, index) => (
          <Box key={index} borderBottom="1px solid gray" p="15px" borderRadius="8px">
            <Flex align="center" mb={4}>
              <Image w="30px" mb="5px" mr="8px" src="/logo.png" />
              <Box p="5px 15px" background="white" borderRadius="16px">
                <Text fontWeight="bold">질문: {item.job_question_kor}</Text>
              </Box>
            </Flex>
            <Flex align="center" mb={4}>
              <FaComment
                style={{
                  marginLeft: '5px',
                  fontSize: '20px',
                  marginRight: '13px',
                  color: 'green',
                }}
              />
              <Box p="5px 15px" background="white" borderRadius="16px">
                <Text>
                  답변: {item.job_answer === '' ? '답변 없음' : item.job_answer}
                </Text>
              </Box>
            </Flex>
          </Box>
        ))}
      </VStack>

      {/* Evaluation Section */}
      <Box mt={8}>
        <Heading as="h3" size="lg" mb={4}>
          평가 결과
        </Heading>

        <SimpleGrid columns={[1, 2]} spacing={4}>
          <Box p="6" border="1px" borderRadius="8px" borderColor="gray.300">
            <Text fontWeight="bold" mb={2}>강점</Text>
            <Text>{reportData ? reportData.strength : ""}</Text>
          </Box>
          <Box p="6" border="1px" borderRadius="8px" borderColor="gray.300">
            <Text fontWeight="bold" mb={2}>약점</Text>
            <Text>{reportData ? reportData.weakness : ""}</Text>
          </Box>
        </SimpleGrid>

        <Box p="6" mt={4} border="1px" borderRadius="8px" borderColor="gray.300">
          <Text fontWeight="bold" mb={2}>AI 요약</Text>
          <Text>{reportData ? reportData.ai_summary : ""}</Text>
        </Box>

        <Box mt={8} p="6" border="1px" borderRadius="8px" borderColor="gray.300">
          <Text fontWeight="bold" mb={2}>문항별 평가</Text>
          <Accordion allowMultiple>
            {Object.entries(evaluationResults).map(([questionNum, evaluation], index) => (
              <AccordionItem key={index}>
                <h2>
                  <AccordionButton>
                    <Box flex="1" textAlign="left">
                      {questionNum}
                    </Box>
                    <AccordionIcon />
                  </AccordionButton>
                </h2>
                <AccordionPanel pb={4}>
                  <SimpleGrid columns={1} spacing={4}>
                    <Box>
                      <Text fontWeight="bold">정확성 (점수: {evaluation.정확성.score})</Text>
                      <Text>{evaluation.정확성.description}</Text>
                    </Box>
                    <Box>
                      <Text fontWeight="bold">직무적합성 및 역량 (점수: {evaluation.직무적합성_역량.score})</Text>
                      <Text>{evaluation.직무적합성_역량.description}</Text>
                    </Box>
                    <Box>
                      <Text fontWeight="bold">논리성 (점수: {evaluation.논리성.score})</Text>
                      <Text>{evaluation.논리성.description}</Text>
                    </Box>
                  </SimpleGrid>
                </AccordionPanel>
              </AccordionItem>
            ))}
          </Accordion>
        </Box>

        {/* Bar Chart for Evaluation */}
        <Box mt={8} p="6" border="1px" borderRadius="8px" borderColor="gray.300">
          <Text fontWeight="bold" mb={4}>문항별 점수 차트</Text>
          <Bar data={chartData} />
        </Box>

        <Box mt={8} p="6" border="1px" borderRadius="8px" borderColor="gray.300">
          <Text fontWeight="bold" mb={2}>결과 점수</Text>
          <Text fontSize="xl">
            총점: {reportData ? reportData.report_score : ""}
            {reportData ? (() => {
              const totalScore = reportData.report_score;
              let level = "";

              if (15 <= totalScore && totalScore <= 20) {
                level = "매우 미흡";
              } else if (21 <= totalScore && totalScore <= 26) {
                level = "미흡";
              } else if (27 <= totalScore && totalScore <= 32) {
                level = "보통";
              } else if (33 <= totalScore && totalScore <= 38) {
                level = "우수";
              } else if (39 <= totalScore && totalScore <= 45) {
                level = "매우 우수";
              } else {
                level = "알 수 없음";
              }

              return ` (${level})`;
            })() : ""}
          </Text>
        </Box>

        <Box mt={4} p="6" border="1px" borderRadius="8px" borderColor="gray.300">
          <Text fontWeight="bold" mb={2}>결과 생성일</Text>
          <Text>{reportData ? formatDate(reportData.report_created) : ""}</Text>
        </Box>
      </Box>
    </Box>
  );
};

export default DetailLog;
