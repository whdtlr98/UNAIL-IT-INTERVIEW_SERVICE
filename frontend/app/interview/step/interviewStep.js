import { Box, Flex, Button, Text, Spinner } from '@chakra-ui/react';
import React, { useState, useEffect } from 'react';
import WebcamComponent from '../components/webcam';
import ChatComponent from '../components/chatComponent';
import SpeechToText from '../components/getaudio';
import { useFetchQuestion } from './hook/getQuestion';
import { useRouter } from 'next/navigation';
import { useFetchAnswer } from './hook/getAnswer';

const InterviewStep = React.memo(() => {
  const router = useRouter();

  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [isRecording, setIsRecording] = useState(false);
  const [timers, setTimers] = useState({ countdown: 10, recording: 5 });
  const [questions, setQuestions] = useState([]);
  const [isInterviewComplete, setIsInterviewComplete] = useState(false);
  const [interviewData, setInterviewData] = useState([]);
  const [loading, setLoading] = useState(true);


  const { questionList, questionAnswerList, interviewId } = useFetchQuestion();

  const { getAnswerFunction, isLoading, answers } = useFetchAnswer();


  useEffect(() => {
    if(answers){
      setLoading(false); // 로딩 상태 비활성화
      router.push('/myPage')
      console.log(answers)
    }
  },[answers])

  useEffect(() => {
    if (questionList.length > 0) {
      setQuestions(questionList);
      setLoading(false);
      startTimers();
    }
  }, [questionList]);

  const startTimers = () => {
    setTimers({ countdown: 10, recording: 5 });
    setIsRecording(false);
  };

  const handleTranscriptUpdate = (newTranscript) => {
    setInterviewData((prev) => [
      ...prev,
      {
        question: questions[currentQuestionIndex],
        solution: questionAnswerList[currentQuestionIndex],
        answer: newTranscript,
      },
    ]);
  };

  // 타이머 및 인터뷰 로직
  useEffect(() => {
    if (loading || isInterviewComplete) return;

    if (timers.countdown > 0 && !isRecording) {
      const countdownInterval = setInterval(() => {
        setTimers((prev) => ({ ...prev, countdown: prev.countdown - 1 }));
      }, 1000);
      return () => clearInterval(countdownInterval);
    } else if (timers.countdown === 0 && !isRecording) {
      setIsRecording(true);
      setTimers((prev) => ({ ...prev, recording: 10 }));
    }
  }, [timers.countdown, isRecording, isInterviewComplete, loading]);

  useEffect(() => {
    if (loading || isInterviewComplete) return;

    if (timers.recording > 0 && isRecording) {
      const recordingInterval = setInterval(() => {
        setTimers((prev) => ({ ...prev, recording: prev.recording - 1 }));
      }, 1000);
      return () => clearInterval(recordingInterval);
    } else if (timers.recording === 0 && isRecording) {
      setIsRecording(false);
      nextQuestion();
    }
  }, [timers.recording, isRecording, isInterviewComplete, loading]);

  const nextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex((prev) => prev + 1);
      setTimers({ countdown: 10, recording: 10 }); // 타이머 초기화
    } else {
      setIsInterviewComplete(true);
    }
  };

  const onSubmitAnswer = () => {
    const answersFromFrontend = interviewData.map((data) => ({
      interview_id: interviewId,
      job_question_kor: data.question,
      job_answer_kor: data.answer,
      job_solution_kor: data.solution,
    }));
    setLoading(true); // 로딩 상태 활성화
    getAnswerFunction({
      interview_id: interviewId,
      answers: answersFromFrontend,
    });
  };
  return (
    <Box>
    <Flex justify={'space-around'} mb={'20px'}>
      <Box maxW={'700px'}>
        <WebcamComponent />
        <Box background={'#DFE2FB'} h={'100px'} minW={'100%'} mt={'30px'}>
          <SpeechToText
            isRecording={isRecording}
            onTranscriptUpdate={handleTranscriptUpdate}
          />
        </Box>
      </Box>
      <Box minW={'40%'} w={'40%'}>
        <Box
          background={'#DFE2FB'}
          h={'450px'}
          p={'40px 0'}
          overflowY={'scroll'}
        >
          {loading ? (
            <Flex justify="center" align="center" h="100%">
              <Spinner size="xl" />
              <Text ml={3}>로딩 중...</Text>
            </Flex>
          ) : (
            <>
              <Text ml={'20px'} fontSize="lg" color="gray.600">
                {isInterviewComplete
                  ? '모든 질문이 완료되었습니다.'
                  : isRecording
                  ? `녹음 중: ${timers.recording}초 남음`
                  : `답변 준비 시간: ${timers.countdown}초`}
              </Text>
              <Box m={'20px'}>
                <Flex alignItems={'center'} ml={'5px'}>
                  <ChatComponent
                    key={currentQuestionIndex}
                    index={currentQuestionIndex}
                    question={questions[currentQuestionIndex]}
                  />
                </Flex>
              </Box>
            </>
          )}
        </Box>
        {loading || isLoading ? (
          <Flex justify="center" align="center" h="100%">
            <Spinner size="xl" />
            <Text ml={3}>로딩 중...</Text>
          </Flex>
        ) : (
          <Button
            w={'100%'}
            h={'100px'}
            background={'#DFE2FB'}
            fontFamily={'inter'}
            mt={'30px'}
            onClick={onSubmitAnswer}
            isDisabled={
              !isInterviewComplete &&
              (isRecording ||
                (timers.countdown > 0 &&
                  interviewData.length !== questions.length))
            }
          >
            {isInterviewComplete && interviewData.length === questions.length
              ? '면접 완료'
              : '진행중'}
          </Button>
        )}
      </Box>
    </Flex>
  </Box>
  );
});

export default InterviewStep;
