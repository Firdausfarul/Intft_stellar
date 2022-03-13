var address; //storing the address or public key
var firsttx; //storing txid for createAccount transaction(first tx, to know the account creator)
var faucetID1;
var faucetID2;

SERVER_URL="https://horizon-testnet.stellar.org"
const server = new StellarSdk.Server(SERVER_URL); 

NFT_code="INT"

imgUrl="?"

apiUrl="https://oaupid.deta.dev/"

//fetching public key from freighter
const retrievePublicKey = async () => {
  let error = "";
  try {
    publicKey = await window.freighterApi.getPublicKey();
  } 
  catch (e) {
    error = e;
  }

  if (error) {
    return error;
  }
  mumu(publicKey); //storing fetched publickey to address
  return publicKey;
};

//storing fetched publickey to address
function mumu(pk){
  address = pk;
  var kon = document.createElement('P'); //printing the address
  kon.innerHTML = "Address : " + pk; 
  document.body.appendChild(kon);
}
function freight(){
    if (window.freighterApi.isConnected()) {
    hidd(); //erasing login button
    retrievePublicKey();
    }
    else{
    alert("Freighter not found, Please Install Freighter First");
  }
}

function rabett(){
  if (!window.rabet) {
    alert("Rabet not found, Please Install Rabet First");
  }
  else{
    hidd(); //erasing login button
    console.log(1000);
    rabet.connect()
    .then(result => mumu(result.publicKey))
    .catch(error => console.error(`Error: ${error}`));
  }
}

//erasing login button
function hidd(){
  var button=document.getElementById('rabeto');
  button.style.display="none";
  var button=document.getElementById('freighter');
  button.style.display="none";
}

async function fetch_nft(){
    account_details= await server.accounts().accountId(address).call()
    NFT_owned = []
    for(let i = 0;i<account_details.balances.length;i++){
        if(account_details.balances[i].asset_type=="liquidity_pool_shares" || account_details.balances[i].asset_type=="native"){
            continue;
        }
        if(account_details.balances[i].asset_code==NFT_code){
            NFT_owned.push(account_details.balances[i].asset_issuer)
        }
        //verification to be added
    } 
    for(let j=0; j< NFT_owned.length;j++){
        nft_details(NFT_owned[j]);
    }
}

async function nft_details(nft_id){
    account_details= await server.accounts().accountId(nft_id).call()
    nft_details=account_details.data_attr
  console.log(nft_details)
    nft_genes=atob(nft_details.genes)
  console.log(nft_genes)
    img64=await axios.get(apiUrl+"img_translator?hex="+nft_genes)
    img64=img64.data.img_str
    var img = document.createElement("img");
    img.src = "data:image/png;base64, "+ img64; 
    img.height = 256; 
    img.width = 256;
    var kon = document.createElement('P');
    kon.innerHTML = "GENES = " + nft_genes + "\n" +  "ID = " + nft_id; 
    document.body.appendChild(kon);
    document.body.appendChild(img);
  
}

async function claimNFT(){
    // Fetch the base fee and the account that will create our transaction
    claimId=[]
    claimBal=await server.claimableBalances().claimant(address).call()
    claimBal=claimBal.records
    for(let i=0; i < claimBal.length;i++){
        claimId.push({
        id: claimBal[i].id,
        issuer: claimBal[i].asset.substring(4)})
    }
  console.log(claimId)
    // Fetch the base fee and the account that will create our transaction
    const [
        {
          max_fee: { mode: fee },
        },
        account,
      ] = await Promise.all([
        server.feeStats(),
        server.loadAccount(address),
      ]);
    const transaction = new StellarSdk.TransactionBuilder(account, {
        fee,
        networkPassphrase: StellarSdk.Networks.TESTNET,
    })
    for(let j=0; j < claimBal.length;j++){
        transaction.addOperation(StellarSdk.Operation.changeTrust({
            asset: new StellarSdk.Asset(NFT_code, claimId[j].issuer)
        })).addOperation(StellarSdk.Operation.claimClaimableBalance({
            balanceId: claimId[j].id
        }))
    }
  xdr = transaction.setTimeout(1000).build().toXDR()
  signAndSubmit(xdr);
}


async function signAndSubmit(xdr){
  console.log("asu")  
  let signedTransaction = "";
    let error = "";
      
    try {
        signedTransaction = await window.freighterApi.signTransaction(xdr, "TESTNET");
    } catch (e) {
        error = e;
    }

    if (error) {
        return error;
    }
    const transactionToSubmit = StellarSdk.TransactionBuilder.fromXDR(
        signedTransaction,
        SERVER_URL
      );
      const responseTransaction = await server.submitTransaction(
        transactionToSubmit
      );
      alert(responseTransaction.hash);
}

async function faucet(){
    req = await axios.get(apiUrl+"faucet?pubkey="+address)
    xdr = req.data.xdr_faucet
    await signAndSubmit(xdr);
}

async function mintGenesis(){
    req = await axios.get(apiUrl + "mint_genesis?pubkey="+ address)
    req = req.data
    xdr = req.xdr_mint
    id1 = req.claimableID1
    id2 = req.claimableID2
    await signAndSubmit(xdr);
  await delay(7000)
    xdrClaim1 = await claimNFT(address, id1)
    await signAndSubmit(xdrClaim1)
    xdrClaim2 = await claimNFT(address, id1)
    await signAndSubmit(xdrClaim2)
}

async function initialize(){
  parent1=parent1.value
  parent2=parent2.value
    req = await axios.get(apiUrl + "initialize?pubkey=" + address + "&parent1="+ parent1 +"&parent2=" +parent2)
    req = req.data
    xdr = req.xdr_init
    await signAndSubmit(xdr)
    breed(req.init_pubkey) 
}

async function breed(init_pubkey){
    req = await axios.get(apiUrl+"breed?init_pubkey=" + init_pubkey)
    req = req.data
    alert("wait 10 seconds before claiming the NFT")
    xdr = await claimNFT(req.claimableId)
    await signAndSubmit(xdr)
}
const delay = ms => new Promise(res => setTimeout(res, ms));