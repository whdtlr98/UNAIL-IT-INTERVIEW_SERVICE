// import { SSMClient, GetParameterCommand } from '@aws-sdk/client-ssm';
// import { fromNodeProviderChain } from '@aws-sdk/credential-providers';

// const ssmClient = new SSMClient({
//   region: process.env.AWS_DEFAULT_REGION || 'ap-northeast-2',
//   credentials: fromNodeProviderChain(),
// });

// export async function getParameterStore(parameterName) {
//   console.log(`Fetching parameter: ${parameterName}`);
//   const command = new GetParameterCommand({
//     Name: parameterName,
//     WithDecryption: true,
//   });

//   try {
//     const response = await ssmClient.send(command);
//     console.log('Parameter fetched successfully:', response.Parameter.Value);
//     return response.Parameter.Value;
//   } catch (error) {
//     console.error('Error fetching parameter:', error.message);
//     console.error('Full error:', JSON.stringify(error, null, 2));
//     return null;
//   }
// }
