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

### 한 줄 요약 : checkout.js를 안전하게, 올바르게 불러오기 위한 빌드업

결제구현 예외처리, 예외처리, 예외처리!

결제 담당 앱 : https://github.com/web-together/Django-Shop/tree/master/order

### 주요 코드 해설

#### [`iamport.py`](https://github.com/web-together/Django-Shop/blob/master/order/iamport.py)

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

#### [`models.py`](https://github.com/web-together/Django-Shop/blob/master/order/models.py)

```
Order
    생략

OrderItem
    생략

class OrderTransaction(models.Model):
    실제 주문 트랜젝션에서 유효하게 다루어질 정보들 
    트랜젝션 정보 그 자체
    
    objects = OrderTransactionManager()


OrderTransactionManager
    OrderTrasaction을 관리하는 manager클래스

    결제정보를 만들고, 조회할 수 있게 한다.
    이 때 결제정보는 hash값으로 암호화하여 생성한다. 

    def create_new
    def get_transaction


def order_payment_validation(sender, instance, created, *args, **kwargs):
    if instance.transaction_id:
        import_transaction = OrderTransaction.objects.get_transaction(merchant_order_id=instance.merchant_order_id)

        merchant_order_id = import_transaction['merchant_order_id']
        imp_id = import_transaction['imp_id']
        amount = import_transaction['amount']

        local_transaction = OrderTransaction.objects.filter(merchant_order_id = merchant_order_id, transaction_id = imp_id,amount = amount).exists()

        if not import_transaction or not local_transaction:
            raise ValueError("비정상 거래입니다.")

# 결제 정보가 생성된 후에 호출할 함수를 연결해준다.
from django.db.models.signals import post_save
post_save.connect(order_payment_validation,sender=OrderTransaction)

```

#### [`views.py`](https://github.com/web-together/Django-Shop/blob/master/order/views.py)

> 유저는 order_create으로 들어간 html에서 결제를 진행하고
> 결제는 OrderCreateAjaxView -> OrderCheckoutAjaxView -> checkout.js -> OrderImpAjaxView 순 진행
> 결제가 완료되면 order_complete으로 이동

```
order_create(request)
    생략

order_complete
    생략

 >> 실 결제를 하는 ajax처리 view들이 order 앱 view의 핵심!

class OrderCreateAjaxView(View):
    로그인 된 사용자인지 (authenticated) 확인    
    장바구니에 담긴 내용을 토대로 주문
    주문 정보 저장 (form.save)
    OrderItem 생성 (OrderItem.objects.create)
    장바구니 지우기 (clear)

class OrderCheckoutAjaxView(View):
    로그인 된 사용자인지 (authenticated) 확인    
    OrderTransaction 객체 생성
    merchant_order_id 반환받음

class OrderImpAjaxView(View):
    merchant_order_id로 실제 거래가 이루어졌는지 확인
    주문 완료시 order_complete 호출 > 주문 완료 html 띄우기
```

### reference

 - [공식 사이트](https://www.iamport.kr/)
 - [공식 repo](https://github.com/iamport/iamport-manual/blob/master/%EC%9D%B8%EC%A6%9D%EA%B2%B0%EC%A0%9C/README.md#211-param-%EC%86%8D%EC%84%B1%EA%B3%B5%ED%86%B5-%EC%86%8D%EC%84%B1)
 - [정리 잘 된 블로그](https://todakandco.tistory.com/10)