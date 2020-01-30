## 아임포트를 이용한 결제연동

> 들어가며

**결제모듈 연동은 진짜 별 것도 아닌데 일단 구현하면 진짜 있어보이는 기능 중 하나다.**

단, 여기서 결제모듈을 어느정도로 구현하는지에 따라 구현에 들어가는 노력이 천지차이로 달라진다.

해커톤, 단기 프로젝트 등 실사용자를 고려하지 않은 프로젝트를 위해서라면 10분만에도 만들 수도 있지만,

실제 사용자들의 사용을 염두하고 결제모듈을 붙인다면 정말정말 많은 코드작업을 해야 할 것이다.

오늘 수업에서는 간단하게 결제창을 띄우는 것까지 구현하는 방법(순한맛)을 알아보고, 

실사용자를 위한 결제모듈 구현 코드(매운맛)는 유인물로 나누어주되,

그 코드가 많고 복잡할 수 있으므로, 큰 그림만 설명할 예정이다.

## tutorial

https://www.iamport.kr/getstarted

## 순한맛 - 간단히 끌어다 쓰기

### 아임포트 가입

### 가맹점코드 확인

### 라이브러리 적용

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

> 해당 js (ajax) 만 적절한 타이밍에 띄워주면 그냥 끝

## 매운맛 - django 실서비스 적용하기 

### 한 줄 요약 : 결제모듈(checkout.js)를 안전하게, 올바르게 불러오기 위한 어마어마한 빌드업

> 예외처리, 예외처리, 예외처리!

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
    주문자 이름, 이메일, 주소, 우편번호(postal code), 도시, 생성날짜, 수정날짜, 결제여부, 쿠폰

OrderItem
    주문에 필요한 제품 정보
    주문정보(바로 위 Order), 상품, 가격, 수량

class OrderTransaction(models.Model):
    실제 주문 트랜젝션에서 유효하게 다루어질 정보들 
    트랜젝션 정보 그 자체

    주문정보(Order), 판매자정보, transaction id, 수량, transaction 상태

    objects = OrderTransactionManager()


OrderTransactionManager
    OrderTrasaction을 관리하는 manager클래스

    결제정보를 만들고, 조회할 수 있게 한다.
    이 때 결제정보는 hash값으로 암호화하여 생성한다. 

    def create_new
    def get_transaction


def order_payment_validation(sender, instance, created, *args, **kwargs):

```

#### [`views.py`](https://github.com/web-together/Django-Shop/blob/master/order/views.py)

> 유저는 order_create으로 들어간 html에서 결제를 진행하고
>
> 결제는 OrderCreateAjaxView -> OrderCheckoutAjaxView -> checkout.js -> OrderImpAjaxView 순 진행
>
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
