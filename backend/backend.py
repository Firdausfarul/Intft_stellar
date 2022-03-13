from stellar_sdk import Keypair,Server, TransactionBuilder, Network, Signer, Asset, xdr, TrustLineFlags, Claimant, ClaimPredicate
import hashlib
import datetime
import secrets
from base64 import b64decode

server = Server("https://horizon-testnet.stellar.org")
base_fee = server.fetch_base_fee()*1000
pregTime = 10 #seconds
masterKey = Keypair.from_secret("SANDPN7OTZYBAPWEQXW2RHKVBFZ6AE2BJESPE2W2XOLGBDNCLKHFHW7X")
BreedIssuer = Keypair.from_secret("SCDLECXOWRXPLA3FHL3XJZVG7WVVSDDVGVSY7AWH5SKXSOIUW7SHYYI5")
AuthToken = Asset("INTAUTH", masterKey.public_key)
BreedToken = Asset("LOVE", BreedIssuer.public_key)
BreedTokenMin = 100
cooldown = 1000 #ledger
NFT_code = "INT"
signer = Signer.ed25519_public_key(account_id=masterKey.public_key, weight=1)

#NFT Identifier = Issuer Public Key
#public endpoint ->
#mint_genesis(pubkey) returns xdr,
#faucet(pubkey) returns (xdr,claimablebalanceID1, claimablebalanceID2) + you need to claim
#initialize(pubkey, parent 1, parent 2) returns xdr
#breed(init_pubKey) return resultGenes

def is_male(genes):
    first_digit = int(genes[:1], 16)
    if (first_digit >= 8):
        return False
    else:
        return True
def mix_genes(genes1, genes2):
    max_genes=0xffffffff
    seed1 = secrets.token_hex(32)
    seed2 = secrets.token_hex(32)
    print(seed1)
    avg = 0.46
    mutate = 0.08
    result = ""
    for i in range(8):
        if(int(seed1[i*8:i*8+8], 16)/max_genes < mutate):
            result = result + seed2[i*8:i*8+8]
        elif(mutate < int(seed1[i*8:i*8+8], 16)/max_genes < mutate+avg):
            average = int((int(genes1[i*8:i*8+8], 16) + int(genes2[i*8:i*8+8], 16))/2)
            result = result + hex(average)[2:]
        elif(mutate+avg < int(seed1[i*8:i*8+8], 16)/max_genes < 1-((mutate+avg)/2)):
            result = result + genes1[i*8:i*8+8]
        else:
            result = result + genes2[i*8:i*8+8]
        print(result)
    return result
def transfer_auth_token(tx, pubkey):
    tx.append_change_trust_op(
        asset=AuthToken,
        source=pubkey
    ).append_set_trust_line_flags_op(
        trustor=pubkey,
        asset=AuthToken,
        set_flags=TrustLineFlags.AUTHORIZED_FLAG,
        source=masterKey.public_key
    ).append_payment_op(
        amount="1",
        asset=AuthToken,
        destination=pubkey,
        source=masterKey.public_key
    ).append_set_trust_line_flags_op(
        trustor=pubkey,
        asset=AuthToken,
        clear_flags=TrustLineFlags.AUTHORIZED_FLAG,
        source=masterKey.public_key
    )
    return tx

def create_acc_change_signer(tx, pubkey):
    tx.append_create_account_op(
        destination=pubkey,
        starting_balance="10"
    ).append_set_options_op(
        master_weight=0,
        source=pubkey,
        signer=signer
    )
    return tx

def mint(tx,user_pubkey, issuer, genes, birthtime, dadId, momId, generation, time):
    claimPredicate = ClaimPredicate.predicate_not(ClaimPredicate.predicate_before_relative_time(time))

    tx=transfer_auth_token(tx, issuer)
    tx.append_manage_data_op(
        data_name="genes",
        data_value=str(genes),
        source=issuer
    ).append_manage_data_op(
        data_name="birthTime",
        data_value=birthtime,
        source=issuer
    ).append_manage_data_op(
        data_name="cooldown",
        data_value="0",
        source=issuer
    ).append_manage_data_op(
        data_name="dadId",
        data_value=dadId,
        source=issuer
    ).append_manage_data_op(
        data_name="momId",
        data_value=momId,
        source=issuer
    ).append_manage_data_op(
        data_name="generation",
        data_value=generation,
        source=issuer
    ).append_create_claimable_balance_op(
        asset=Asset(NFT_code, issuer),
        source=issuer,
        amount="0.0000001",
        claimants=[Claimant(destination=user_pubkey, predicate=claimPredicate)]
    )

    return tx

def mint_genesis(user_pubkey):
    nft_temp1 = Keypair.random()
    nft_temp2 = Keypair.random()

    time_now=datetime.datetime.now()
    genes1=hashlib.sha256(str.encode(str(time_now))).hexdigest()
    genes2=hashlib.sha256(str.encode(genes1)).hexdigest()
    print(bytes.fromhex(genes1))

    acc_loaded=server.load_account(user_pubkey)
    current_ledger = server.ledgers().order(True).call()['_embedded']['records'][0]["sequence"]
    tx = TransactionBuilder(
        source_account=acc_loaded,
        network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
        base_fee=base_fee,
    ).set_timeout(1000)
    tx = create_acc_change_signer(tx, nft_temp1.public_key)
    tx = create_acc_change_signer(tx, nft_temp2.public_key)
    tx = mint(
        tx=tx,
        user_pubkey=user_pubkey,
        issuer=nft_temp1.public_key,
        genes=genes1,
        birthtime=str(current_ledger),
        dadId="Genesis",
        momId="Genesis",
        generation="0",
        time=1
    )
    tx = mint(
        tx=tx,
        user_pubkey=user_pubkey,
        issuer=nft_temp2.public_key,
        genes=genes2,
        birthtime=str(current_ledger),
        dadId="Genesis",
        momId="Genesis",
        generation="0",
        time=1
    ).append_change_trust_op(
        asset=Asset(NFT_code, nft_temp1.public_key)
    ).append_change_trust_op(
        asset=Asset(NFT_code, nft_temp2.public_key)
    )
    tx=tx.build()
    claimId1=tx.transaction.get_claimable_balance_id(14)
    print(claimId1)
    claimId2=tx.transaction.get_claimable_balance_id(25)
    print(claimId2)
    tx.sign(masterKey.secret)
    tx.sign(nft_temp1.secret)
    tx.sign(nft_temp2.secret)
    return (tx.to_xdr() , claimId1, claimId2)

def initialize(user_pubkey, dadId, momId):
    init_acc=Keypair.random()
    loaded_acc=server.load_account(user_pubkey)
    tx = TransactionBuilder(
        source_account=loaded_acc,
        network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
        base_fee=base_fee,
    ).set_timeout(1000).append_create_account_op(
        destination=init_acc.public_key,
        starting_balance="10"
    ).append_change_trust_op(
        asset=BreedToken,
        source=init_acc.public_key,
    ).append_change_trust_op(
        asset=Asset(NFT_code, dadId),
        source=init_acc.public_key,
    ).append_change_trust_op(
        asset=Asset(NFT_code, momId),
        source=init_acc.public_key,
    ).append_payment_op(
        destination=init_acc.public_key,
        asset=Asset(NFT_code, dadId),
        amount="0.0000001"
    ).append_payment_op(
        destination=init_acc.public_key,
        asset=Asset(NFT_code, momId),
        amount="0.0000001"
    ).append_payment_op(
        destination=init_acc.public_key,
        asset=BreedToken,
        amount=str(BreedTokenMin)
    ).append_set_options_op(
        master_weight=0,
        source=init_acc.public_key,
        signer=signer
    )
    tx=tx.build()
    tx.sign(init_acc.secret)
    return (tx.to_xdr(), init_acc.public_key)

def faucet(user_pubkey):
    loaded_acc=server.load_account(user_pubkey)
    tx = TransactionBuilder(
        source_account=loaded_acc,
        network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
        base_fee=base_fee,
    ).set_timeout(1000).append_change_trust_op(
        asset=BreedToken,
    ).append_payment_op(
        source=BreedIssuer.public_key,
        destination=user_pubkey,
        asset=BreedToken,
        amount="1000"
    )
    tx=tx.build()
    tx.sign(BreedIssuer.secret)
    return tx.to_xdr()

def breed(init_pubkey):
    user_pubkey=server.transactions().for_account(init_pubkey).call()["_embedded"]["records"][0]["source_account"]
    parentsId=[]
    acc_details=server.accounts().account_id(init_pubkey).call()
    eligible=True
    #Checking eligibility
    signer=acc_details['signers']
    bal=acc_details['balances']
    sign_eligibility1=len(signer)!=2
    if(len(signer)!=2):
        eligible=False
    else:
        if (signer[0]['key']==init_pubkey):
            if(signer[0]['weight']!=0):
                eligible=False
        if (signer[1]['key']==init_pubkey):
            if (signer[1]['weight'] != 0):
                eligible = False
    for i in range(len(bal)-1):
        if(bal[i]['asset_code']==NFT_code):
            parentsId.append(bal[i]['asset_issuer'])
    parent1_details = server.accounts().account_id(parentsId[0]).call()
    current_ledger = server.ledgers().order(True).call()['_embedded']['records'][0]["sequence"]
    parent2_details = server.accounts().account_id(parentsId[1]).call()
    fake_nft1=True
    for i in range(len(parent1_details['balances'])-1):
        if(parent1_details['balances'][i]['asset_code']==AuthToken.code and parent1_details['balances'][i]['asset_issuer']==AuthToken.issuer and parent1_details['balances'][i]['balance']=="1.0000000"):
            fake_nft1=False
    fake_nft2 = True
    for i in range(len(parent2_details['balances']) - 1):
        if (parent2_details['balances'][i]['asset_code'] == AuthToken.code and parent2_details['balances'][i][
            'asset_issuer'] == AuthToken.issuer and parent2_details['balances'][i]['balance'] == "1.0000000"):
            fake_nft2 = False
    if(fake_nft1 or fake_nft2):
        return (0, 0)

    parent1_genes=b64decode(parent1_details['data']['genes']).decode('utf-8')
    parent1_generation=b64decode(parent1_details['data']['generation']).decode('utf-8')
    parent2_genes = b64decode(parent2_details['data']['genes']).decode('utf-8')
    parent2_generation = b64decode(parent2_details['data']['generation']).decode('utf-8')

    parent1_cd=b64decode(parent1_details['data']['cooldown']).decode('utf-8')
    parent2_cd= b64decode(parent2_details['data']['cooldown']).decode('utf-8')
    if(int(parent1_cd) > current_ledger or int(parent2_cd) > current_ledger):
        return (0, 0)


    parent1_is_male=is_male(parent1_genes)
    parent2_is_male=is_male(parent2_genes)
    if(parent1_is_male==parent2_is_male):
        return (0, 0)

    offspringMom_num=str(len(parent1_details['data'])-6)
    offspringDad_num = str(len(parent2_details['data']) - 6)

    if(parent1_is_male):
        offspringDad_num, offspringMom_num = offspringMom_num, offspringMom_num

    momId=parentsId[0]
    dadId=parentsId[1]
    if(parent1_is_male):
        momId, dadId = dadId, momId

    result_generation = max(int(parent1_generation), int(parent2_generation))+1
    result_genes = mix_genes(parent1_genes, parent2_genes)

    loaded_acc=server.load_account(init_pubkey)
    tx = TransactionBuilder(
        source_account=loaded_acc,
        network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
        base_fee=base_fee,
    ).set_timeout(1000)
    tx = mint(
        tx=tx,
        user_pubkey=user_pubkey,
        issuer=init_pubkey,
        genes=result_genes,
        birthtime=str(current_ledger),
        dadId=dadId,
        momId=momId,
        generation=str(result_generation),
        time=pregTime
    ).append_manage_data_op(
        source=dadId,
        data_name="cooldown",
        data_value=str(current_ledger+cooldown)
    ).append_manage_data_op(
        source=momId,
        data_name="cooldown",
        data_value=str(current_ledger+cooldown)
    ).append_manage_data_op(
        source=dadId,
        data_name="offspring"+offspringDad_num,
        data_value=init_pubkey
    ).append_manage_data_op(
        source=momId,
        data_name="offspring"+offspringMom_num,
        data_value=init_pubkey
    ).append_payment_op(
        asset=Asset(NFT_code, momId),
        destination=user_pubkey,
        amount="0.0000001"
    ).append_payment_op(
        asset=Asset(NFT_code, dadId),
        destination=user_pubkey,
        amount="0.0000001"
    ).append_payment_op(
        asset=BreedToken,
        destination=BreedToken.issuer,
        amount="100"
    ).build()
    claimableId=tx.transaction.get_claimable_balance_id(10)
    tx.sign(masterKey.secret)
    server.submit_transaction(tx)
    return (result_genes, claimableId)