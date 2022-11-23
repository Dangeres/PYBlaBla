import requests
import uuid
import json


class Blablacar:
    
    def __init__(self, login: str or None = None, password: str or None = None) -> None:
        """
            :param login: str or None* (by default is None)
            :param password: str or None* (by default is None)

            :returns: None
        """

        self.login = login
        self.password = password
        self.session = requests.session()

        res = self.session.get(
            url = 'https://www.blablacar.ru/',
            headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-CA,en;q=0.9,ru-RU;q=0.8,ru;q=0.7,en-GB;q=0.6,en-US;q=0.5',
                'cache-control': 'no-cache',
                'pragma': 'no-cache',
                'sec-ch-device-memory': '8',
                'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
                'sec-ch-ua-arch': '"x86"',
                'sec-ch-ua-full-version-list': '"Google Chrome";v="107.0.5304.107", "Chromium";v="107.0.5304.107", "Not=A?Brand";v="24.0.0.0"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-model': '""',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
            }
        )

        if dict(self.session.cookies).get('vstr_id'):
            self.session.headers.update({
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
                'x-client': 'SPA|1.0.0',
                'x-blablacar-accept-endpoint-version': '2',
                'x-currency': 'RUB',
                'x-forwarded-proto': 'https',
                'x-locale': 'ru_RU',
                'x-visitor-id': self.return_visitor_id(),
                'x-correlation-id': self.generate_uid(),
                'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
            })

            self.session.headers.update({
                'authorization': 'Bearer ' + self.get_secure_token(),
                'accept': 'application/json',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'ru_RU',
            })


    def generate_uid(self):
        """
            Генерирует uuid4
            
            :returns: uuid4 -> str
        """

        return str(uuid.uuid4())


    def return_visitor_id(self) -> str:
        """
            Ищет города внутри сервиса блаблакар по введенному названию пользователя
            
            :returns: x-visitor-id from cookie -> str
        """

        return dict(self.session.cookies).get('vstr_id', '')



    def get_secure_token(self):
        """
            Получает токен безопасности
            
            :returns: authorization barerer from cookie -> str
        """

        # try:
        #     temp = self.session.post(
        #         url = 'https://auth.blablacar.ru/secure-token',
        #         data = {
        #             'client_id': "spa-prod",
        #             'client_secret': "Osz1eNwzXw1zTmSBeZVJWhICx9q7GveF612YBUQXTftvFk8gdPEzcXBUpCf4X651QwsdFj90HObYYoFCkDIvrv0j65leAUkdJXpn",
        #             'grant_type': "client_credentials",
        #         },
        #     )

        #     return temp.json().get('access_token', '')
        # except Exception as e:
        #     print(e)
        
        return dict(self.session.cookies).get('app_token', '')


    def find_city(self, name: str) -> list:
        """
            Ищет города внутри сервиса блаблакар по введенному названию пользователя
            
            :param name: str название города
            :returns: list найденных городов после поиска на сайте
        """

        try:
            temp = self.session.get(
                url = 'https://edge.blablacar.ru/location/suggestions',
                params = {
                    'locale': 'ru_RU',
                    'query': name,
                },
            )

            return temp.json()
        except Exception as e:
            print(e)
        
        return []


    def find_trip(self, from_place_id: str = None, to_place_id: str = None, departure_date: str = '', requested_seats: str = '1', passenger_gender: str = 'UNKNOWN') -> list:
        """
            Ищет доступные поездки из города from_place_id в город to_place_id, в дату departure_date, количество мест requested_seats
            
            :param from_place_id: str айди города откуда стартуем
            :param to_place_id: str название города куда едем
            :param departure_date: str дата в формате 2022-11-23
            :param requested_seats: str количество доступных мест
            :param passenger_gender: str пол пассажиров
            :returns: list найденные поездки после поиска на сайте
        """

        result = []
        temp_result = {}
        from_cursor = None
        parametrs = {
            'from_place_id': from_place_id,
            'to_place_id': to_place_id,
            'departure_date': departure_date,
            'requested_seats': requested_seats,
            'passenger_gender': passenger_gender,
            'search_uuid': self.generate_uid(),
        }

        while True:
            try:
                temp = self.session.get(
                    url = 'https://edge.blablacar.ru/trip/search/v7',
                    params = parametrs,
                )

                tmp = json.loads(temp.text)

                for trip in tmp.get('trips', []):
                    temp_result[trip['multimodal_id']['id']] = {
                        "id": trip['multimodal_id']['id'],
                        "source": trip['multimodal_id']['source'],
                        "total_duration": trip.get('total_duration'),
                        "publishing_profile": trip.get('publishing_profile'),
                        "waypoints": trip.get('waypoints'),
                        "disabled_selection": trip.get('disabled_selection'),
                        "monetization_price": trip.get('monetization_price'),
                        "amenities": trip.get('amenities'),
                        "price_details": trip.get('price_details'),
                        "highlights": trip.get('highlights'),
                        "tags": trip.get('tags'),
                    }

                if tmp.get('pagination', {}).get('next_cursor'):
                    parametrs.update(
                        {
                            'from_cursor': from_cursor,
                        }
                    )

                    from_cursor = tmp.get('pagination', {}).get('next_cursor')
                
                else:
                    break

            except Exception as e:
                print(e)

        for i in temp_result:
            result.append(
                temp_result[i]
            )
        
        return result



if __name__ == '__main__':
    blaobject = Blablacar()
    result = blaobject.find_city('Москва')
    result2 = blaobject.find_city('Санкт Питербург')
    
    t_result = blaobject.find_trip(
        from_place_id = result[0]['id'],
        to_place_id = result2[0]['id'],
        departure_date = '2022-11-23',
        requested_seats = '1',
    )

    print(t_result)