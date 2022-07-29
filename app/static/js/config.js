const key = JSON.parse(document.getElementById('client-key').innerHTML);

const urlParams = new URLSearchParams(window.location.search);
const sessionId = urlParams.get('sessionId');
const redirectResult = urlParams.get('redirectResult');

async function callServer(url, data) {
	const res = await fetch(url, {
		method: 'POST',
		body: data ? JSON.stringify(data) : '',
		headers: {
			'Content-Type': 'application/json'
		}
	});

	return await res.json();
}

async function start() {
	try {
		const checkoutRes = await callServer('/api/sessions');
		const checkout = await create(checkoutRes)
		const dropin = checkout.create('dropin').mount('#dropin-container');
	} catch (error) {
		console.error(error);
		alert(error);
	}
}

async function finish() {
    try {
        const checkout = await create({id: sessionId});
        checkout.submitDetails({details: {redirectResult}});
    } catch (error) {
        console.error(error);
        alert(error);
    }
}

async function create(session) {
    const configuration = {
        clientKey: key,
        locale: 'en_US',
        environment: 'test',
        showPayButton: true,
        session: session,
        onPaymentCompleted: (result, component) => {
            handleServerResponse(result, component);
        },
        onError: (error, component) => {
            console.error(error.name, error.message, error.stack, component);
        },
        paymentMethodsConfiguration: {
            card:
            {
                hasHolderName: true,
                holderNameRequired: true,
                storePaymentMethod: true
            }
        }
    };
    return new AdyenCheckout(configuration);
}


function handleServerResponse(res, component) {
	if (res.action) {
		component.handleAction(res.action);
	} else {
		switch (res.resultCode) {
			case 'Pending':
            case 'Received':
            case 'Authorised':
				window.location.href = '/result/success';
				break;
			case 'Error':
            case 'Refused':
				window.location.href = '/result/failed';
				break;
            case 'Cancelled':
                window.location.href = '/result/failed';
                break;
		}
	}
}

if (!sessionId) {
    start();
}
else {
    finish();
}