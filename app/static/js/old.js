const key = JSON.parse(document.getElementById('client-key').innerHTML);

const urlParams = new URLSearchParams(window.location.search);

async function callServer(url, data)
{
	const res = await fetch(url, {
		method: 'POST',
		body: data ? JSON.stringify(data) : '',
		headers: {
			'Content-Type': 'application/json'
		}
	});
	return await res.json();
}

async function handleSubmission(state, component, url) {
	try {
		const res = await callServer(url, state.data);
		const serverRes = handleServerResponse(res, component);
	} catch (error) {
		console.error(error);
		alert(error);
	}
}

async function start() {
	try {
		const getMethods = await callServer('/api/methods');
		const checkout = await create(getMethods)
		const dropin = checkout.create('dropin').mount('#dropin-container');
	} catch (error) {
		console.error(error);
		alert(error);
	}
}

async function create(methods) {
    const configuration = {
        paymentMethodsResponse: methods,
        clientKey: key,
        locale: 'en-US',
        environment: 'test',
        paymentMethodsConfiguration: {
          card: {
            hasHolderName: true,
            holderNameRequired: true,
          }
        },
        onSubmit: (state, component) => {
          console.log(state);
          if (state.isValid) {
            handleSubmission(state, component, '/api/makePayment');
          }
        },
        onAdditionalDetails: (state, component) => {
          handleSubmission(state, component, '/api/details');
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

start();