import requests
import json
from typing import Optional, Dict, Any, Callable
from logger_config import get_logger

logger = get_logger('dify_client')


class DifyClient:
    def __init__(self, api_key: str, base_url: str = "https://api.dify.ai/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.current_task_id = None

    def send_message(
        self,
        query: str,
        user: str,
        conversation_id: Optional[str] = None,
        inputs: Optional[Dict[str, Any]] = None,
        response_mode: str = "blocking",
        on_message: Optional[Callable[[str], None]] = None,
        on_finished: Optional[Callable[[], None]] = None,
        on_error: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        # 检查base_url是否已经包含/chat-messages路径
        if self.base_url.endswith('/chat-messages'):
            url = self.base_url
        else:
            url = f"{self.base_url}/chat-messages"
        logger.debug(f"最终请求URL: {url}")
        
        logger.debug(f"准备发送请求到: {url}")
        logger.debug(f"API Key: {self.api_key[:10]}...")
        logger.debug(f"Query: {query}")
        logger.debug(f"User: {user}")
        logger.debug(f"Conversation ID: {conversation_id}")
        logger.debug(f"Response Mode: {response_mode}")
        
        payload = {
            "query": query,
            "user": user,
            "response_mode": response_mode,
            "inputs": inputs or {}
        }
        
        if conversation_id:
            payload["conversation_id"] = conversation_id
        
        logger.debug(f"Payload: {json.dumps(payload, ensure_ascii=False)}")
        
        try:
            logger.info("开始发送请求...")
            logger.debug(f"最终构造的URL: {url}")
            logger.debug(f"请求方法: POST")
            logger.debug(f"请求头: {json.dumps(self.headers, ensure_ascii=False)}")
            logger.debug(f"请求体: {json.dumps(payload, ensure_ascii=False)}")
            
            if response_mode == "streaming":
                logger.info("使用流式请求模式")
                return self._send_streaming_request(url, payload, on_message, on_finished, on_error)
            else:
                logger.info("使用阻塞请求模式")
                return self._send_blocking_request(url, payload)
                
        except requests.exceptions.Timeout:
            logger.error("请求超时")
            raise Exception("Dify API请求超时")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"连接失败: {str(e)}")
            raise Exception(f"Dify API连接失败: {str(e)}")
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP错误: {str(e)}")
            if hasattr(e, 'response'):
                logger.debug(f"响应内容: {e.response.text}")
                raise Exception(f"Dify API HTTP错误: {e.response.status_code} - {e.response.text}")
            else:
                raise Exception(f"Dify API HTTP错误: {str(e)}")
        except requests.exceptions.RequestException as e:
            logger.error(f"请求异常: {str(e)}")
            raise Exception(f"Dify API请求失败: {str(e)}")

    def _send_blocking_request(self, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(url, headers=self.headers, json=payload, timeout=60)
        logger.debug(f"响应状态码: {response.status_code}")
        
        response.raise_for_status()
        
        result = response.json()
        logger.debug(f"响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        return result

    def _send_streaming_request(
        self,
        url: str,
        payload: Dict[str, Any],
        on_message: Optional[Callable[[str], None]],
        on_finished: Optional[Callable[[], None]],
        on_error: Optional[Callable[[str], None]]
    ) -> Dict[str, Any]:
        response = requests.post(url, headers=self.headers, json=payload, stream=True, timeout=60)
        logger.debug(f"响应状态码: {response.status_code}")
        
        response.raise_for_status()
        
        full_answer = ""
        task_id = None
        
        for line in response.iter_lines():
            if not line:
                continue
            
            line = line.decode('utf-8')
            
            if line.startswith('data: '):
                data_str = line[6:]
                try:
                    data = json.loads(data_str)
                    
                    if data.get('event') == 'message':
                        answer = data.get('answer', '')
                        full_answer += answer
                        if on_message:
                            on_message(answer)
                        logger.debug(f"收到消息片段: {answer[:50]}...")
                    
                    elif data.get('event') == 'message_end':
                        task_id = data.get('task_id')
                        self.current_task_id = task_id
                        logger.debug(f"消息结束, Task ID: {task_id}")
                        if on_finished:
                            on_finished()
                    
                    elif data.get('event') == 'error':
                        error_msg = data.get('message', '未知错误')
                        logger.error(f"流式错误: {error_msg}")
                        if on_error:
                            on_error(error_msg)
                
                except json.JSONDecodeError as e:
                    logger.error(f"JSON解析错误: {e}")
        
        logger.debug(f"完整响应: {full_answer[:100]}...")
        
        return {
            "answer": full_answer,
            "conversation_id": None,
            "task_id": task_id
        }

    def stop_generation(self) -> bool:
        if not self.current_task_id:
            logger.debug("没有正在进行的任务")
            return False
        
        url = f"{self.base_url}/chat-messages/{self.current_task_id}/stop"
        logger.debug(f"停止生成请求: {url}")
        
        try:
            response = requests.post(url, headers=self.headers, timeout=10)
            logger.debug(f"停止响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                logger.info("停止成功")
                self.current_task_id = None
                return True
            else:
                logger.warning(f"停止失败: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"停止请求异常: {str(e)}")
            return False

    def get_conversation_id(self, response: Dict[str, Any]) -> Optional[str]:
        return response.get("conversation_id")

    def get_answer(self, response: Dict[str, Any]) -> str:
        if response.get("answer"):
            return response["answer"]
        return ""
