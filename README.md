## 아임포트를 이용한 결제연동

## tutorial

https://www.iamport.kr/getstarted

## 실습 - 간단히 끌어다 쓰기

라이브러리 적용

parameter 의미 알기

```
IMP.init('가맹점식별코드');
```

```
IMP.request_pay({
    pg : 'html5_inicis',
    pay_method : 'card',
    merchant_uid : 'merchant_' + new Date().getTime(),
    name : '주문명:결제테스트',
    amount : 14000,
    buyer_email : 'iamport@siot.do',
    buyer_name : '구매자이름',
    buyer_tel : '010-1234-5678',
    buyer_addr : '서울특별시 강남구 삼성동',
    buyer_postcode : '123-456'
}, function(rsp) {
    if ( rsp.success ) {
        var msg = '결제가 완료되었습니다.';
        msg += '고유ID : ' + rsp.imp_uid;
        msg += '상점 거래ID : ' + rsp.merchant_uid;
        msg += '결제 금액 : ' + rsp.paid_amount;
        msg += '카드 승인번호 : ' + rsp.apply_num;
    } else {
        var msg = '결제에 실패하였습니다.';
        msg += '에러내용 : ' + rsp.error_msg;
    }

    alert(msg);
});
```

## 책 - django 실서비스 적용하기 

https://github.com/web-together/Django-Shop/tree/master/order

주요 코드 해설

[`iamport.py`](https://github.com/web-together/Django-Shop/blob/master/order/iamport.py)

```
get_token
    settings.py에 등록한 key, secret 토대로 토큰값을 받아온다
    이 때 토큰 받아오는 url은 https://api.iamport.kr/users/getToken

payment_prepare
    get_token을 통해 토큰값 받아오고, 그 토큰과 
    order정보, 갯수가 담긴 데이터 (access data)를
    결제를 준비 url로 보낸다.
    이 때 결제를 준비하는 url은 https://api.iamport.kr/payments/prepare

find_transaction
    트랜젝션이 이루어졌는지 확인
    즉, 실제로 거래가 결과적으로 이루어졌는지 조회

    order_id를 통해 결제 내역 조회

    이 때 결제를 조회하는 url은 url = "https://api.iamport.kr/payments/find/"+order_id

    결제가 완료되었음을 확인한다면 그제서야 DB에 결제내역 저장
```

### reference

 - [공식 사이트](https://www.iamport.kr/)
 - [공식 repo](https://github.com/iamport/iamport-manual/blob/master/%EC%9D%B8%EC%A6%9D%EA%B2%B0%EC%A0%9C/README.md#211-param-%EC%86%8D%EC%84%B1%EA%B3%B5%ED%86%B5-%EC%86%8D%EC%84%B1)
 - [정리 잘 된 블로그](https://todakandco.tistory.com/10)