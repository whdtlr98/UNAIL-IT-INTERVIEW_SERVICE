import { useGetInterviewReport } from '@/app/api/useInterviewClient';
import { useEffect, useState } from 'react';

export const GetInterviewReport = (interviewId) => {
  const [reportData, setReportData] = useState();
  const { data: report, isError: reportError } =
    useGetInterviewReport(interviewId);

  useEffect(() => {
    if (report) {
      setReportData(report);
    }
  }, [report]);

  useEffect(() => {
    if (reportError) {
      console.log('결과를 로드할 수 없습니다.');
    }
  }, [reportError]);

  return {
    reportData,
  };
};
