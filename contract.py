import smartpy as sp

#marketplace contract
class marketplace_contract(sp.Contract):
    #storage
    def __init__(self):
        self.init(
            #administrator
            admin = sp.test_account("admin").address,
            trade_val  = sp.nat(0),
            
            fees = sp.tez(0),
            gen_user_data = sp.big_map(l = {}, tkey = sp.TAddress, tvalue = sp.TRecord(badge = sp.TString, traded_amount = sp.TNat)),

            nft_partners_contracts = sp.big_map(l = {}, tkey = sp.TString, tvalue = sp.TAddress),
            
            nft_data = sp.big_map(l = {}, tkey = sp.TRecord(user_addr = sp.TAddress, nft_con_data = sp.TAddress, token_id = sp.TNat), tvalue = sp.TRecord(price = sp.TMutez, is_for_sale = sp.TBool)),
            
        )
    @sp.entry_point
    def add_partners(self, params):
        sp.verify(sp.sender == self.data.admin, "NOT AN ADMIN")
        self.data.nft_partners_contracts[params.dictkey] = params.dictvalue
        
    @sp.entry_point
    def direct_transfer_nft(self, params):
        #NFT direct transfer
        direct_transfer_arg = sp.local("direct_transfer_arg", [
            sp.record(
                from_ = sp.sender,
                txs = [
                    sp.record(
                        to_ = params.reciever,
                        token_id = params.token_id,
                        amount = sp.nat(1)
                    )
                ]
            )
        ])

        dir_trans_nft = sp.contract(
            sp.TList(sp.TRecord(from_ = sp.TAddress, txs = sp.TList(sp.TRecord(amount = sp.TNat, to_ = sp.TAddress, token_id = sp.TNat).layout(("to_", ("token_id", "amount")))))),
            params.nft_con_addr,
            entry_point = 'transfer'
        ).open_some()

        sp.transfer(direct_transfer_arg.value, sp.mutez(0), dir_trans_nft)
        pass


    @sp.entry_point
    def buy_nft(self,params):
        #check nft is_for_sale
        sp.verify(self.data.nft_data[sp.record(user_addr = params.seller_addr, nft_con_data = params.nft_con_addr, token_id = params.token_id)].is_for_sale == sp.bool(True), "NFT NOT FOR SALE")

        #amount in nat conversion
        self.data.trade_val = sp.utils.mutez_to_nat(sp.amount)
        self.data.trade_val = self.data.trade_val / sp.nat(1000000)
        
        #checking user data in contract stoarage
        sp.if self.data.gen_user_data.contains(sp.sender):
            sp.if self.data.gen_user_data[sp.sender].badge == sp.string("Bronze"):            
                self.data.fees = sp.split_tokens(self.data.nft_data[sp.record(user_addr = params.seller_addr, nft_con_data = params.nft_con_addr, token_id = params.token_id)].price, 2, 100)
                sp.verify(sp.amount == self.data.nft_data[sp.record(user_addr = params.seller_addr, nft_con_data = params.nft_con_addr, token_id = params.token_id)].price + self.data.fees, "AMOUNT INVALID")
                
                sp.if (self.data.trade_val > sp.nat(100)) & (self.data.trade_val <= sp.nat(1000)):
                    self.data.gen_user_data[sp.sender] = sp.record(badge = sp.string("Gold"), traded_amount = self.data.gen_user_data[sp.sender].traded_amount + self.data.trade_val)                   

                sp.if (self.data.trade_val > sp.nat(1000)) & (self.data.trade_val <= sp.nat(3000)):
                    self.data.gen_user_data[sp.sender] = sp.record(badge = sp.string("Gold"), traded_amount = self.data.gen_user_data[sp.sender].traded_amount + self.data.trade_val)                   

                sp.if (self.data.trade_val > sp.nat(3000)):
                    self.data.gen_user_data[sp.sender] = sp.record(badge = sp.string("Platinum"), traded_amount = self.data.gen_user_data[sp.sender].traded_amount + self.data.trade_val)                   
            sp.else:
                sp.if self.data.gen_user_data[sp.sender].badge == sp.string("Silver"):
                    self.data.fees = sp.split_tokens(self.data.nft_data[sp.record(user_addr = params.seller_addr, nft_con_data = params.nft_con_addr, token_id = params.token_id)].price, 15, 1000)
                    sp.verify(sp.amount == self.data.nft_data[sp.record(user_addr = params.seller_addr, nft_con_data = params.nft_con_addr, token_id = params.token_id)].price + self.data.fees, "AMOUNT INVALID")

                    sp.if (self.data.trade_val > sp.nat(1000)) & (self.data.trade_val <= sp.nat(3000)):
                        self.data.gen_user_data[sp.sender] = sp.record(badge = sp.string("Gold"), traded_amount = self.data.gen_user_data[sp.sender].traded_amount + self.data.trade_val)                   

                    sp.if (self.data.trade_val > sp.nat(3000)):
                        self.data.gen_user_data[sp.sender] = sp.record(badge = sp.string("Platinum"), traded_amount = self.data.gen_user_data[sp.sender].traded_amount + self.data.trade_val)                   
                sp.else:
                    sp.if self.data.gen_user_data[sp.sender].badge == sp.string("Gold"):
                        self.data.fees = sp.split_tokens(self.data.nft_data[sp.record(user_addr = params.seller_addr, nft_con_data = params.nft_con_addr, token_id = params.token_id)].price, 1, 100)
                        sp.verify(sp.amount == self.data.nft_data[sp.record(user_addr = params.seller_addr, nft_con_data = params.nft_con_addr, token_id = params.token_id)].price + self.data.fees, "AMOUNT INVALID")

                        sp.if (self.data.trade_val > sp.nat(3000)):
                            self.data.gen_user_data[sp.sender] = sp.record(badge = sp.string("Platinum"), traded_amount = self.data.gen_user_data[sp.sender].traded_amount + self.data.trade_val)                   
                    sp.else:
                        sp.if self.data.gen_user_data[sp.sender].badge == sp.string("Platinum"):
                            self.data.fees = sp.split_tokens(self.data.nft_data[sp.record(user_addr = params.seller_addr, nft_con_data = params.nft_con_addr, token_id = params.token_id)].price, 5, 1000)
                            sp.verify(sp.amount == self.data.nft_data[sp.record(user_addr = params.seller_addr, nft_con_data = params.nft_con_addr, token_id = params.token_id)].price + self.data.fees, "AMOUNT INVALID")                                                
            pass
        sp.else:
            self.data.gen_user_data[sp.sender] = sp.record(badge = sp.string("Bronze"), traded_amount = self.data.trade_val)
            
            sp.if self.data.gen_user_data[sp.sender].traded_amount <= sp.nat(100):
                self.data.gen_user_data[sp.sender] = sp.record(badge = sp.string("Bronze"), traded_amount = self.data.trade_val)
                self.data.fees = sp.split_tokens(self.data.nft_data[sp.record(user_addr = params.seller_addr, nft_con_data = params.nft_con_addr, token_id = params.token_id)].price, 2, 100)
                sp.verify(sp.amount == self.data.nft_data[sp.record(user_addr = params.seller_addr, nft_con_data = params.nft_con_addr, token_id = params.token_id)].price + self.data.fees, "AMOUNT INVALID")

            sp.if (self.data.gen_user_data[sp.sender].traded_amount > sp.nat(100)) & (self.data.gen_user_data[sp.sender].traded_amount <= sp.nat(1000)):
                self.data.gen_user_data[sp.sender] = sp.record(badge = sp.string("Silver"), traded_amount = self.data.trade_val)
                self.data.fees = sp.split_tokens(self.data.nft_data[sp.record(user_addr = params.seller_addr, nft_con_data = params.nft_con_addr, token_id = params.token_id)].price, 15, 1000)
                sp.verify(sp.amount == self.data.nft_data[sp.record(user_addr = params.seller_addr, nft_con_data = params.nft_con_addr, token_id = params.token_id)].price + self.data.fees, "AMOUNT INVALID")
            
            sp.if (self.data.gen_user_data[sp.sender].traded_amount > sp.nat(1000)) & (self.data.gen_user_data[sp.sender].traded_amount <= sp.nat(3000)):
                self.data.gen_user_data[sp.sender] = sp.record(badge = sp.string("Gold"), traded_amount = self.data.trade_val)
                self.data.fees = sp.split_tokens(self.data.nft_data[sp.record(user_addr = params.seller_addr, nft_con_data = params.nft_con_addr, token_id = params.token_id)].price, 1, 100)
                sp.verify(sp.amount == self.data.nft_data[sp.record(user_addr = params.seller_addr, nft_con_data = params.nft_con_addr, token_id = params.token_id)].price + self.data.fees, "AMOUNT INVALID")
            
            sp.if (self.data.gen_user_data[sp.sender].traded_amount > sp.nat(3000)):
                self.data.gen_user_data[sp.sender] = sp.record(badge = sp.string("Platinum"), traded_amount = self.data.trade_val)
                self.data.fees = sp.split_tokens(self.data.nft_data[sp.record(user_addr = params.seller_addr, nft_con_data = params.nft_con_addr, token_id = params.token_id)].price, 5, 1000)
                sp.verify(sp.amount == self.data.nft_data[sp.record(user_addr = params.seller_addr, nft_con_data = params.nft_con_addr, token_id = params.token_id)].price + self.data.fees, "AMOUNT INVALID")                        
            pass
                    
        #transfer nft
        transfer_arg = sp.local("transfer_arg", [
            sp.record(
                from_ = params.seller_addr,
                txs = [
                    sp.record(
                        to_ = sp.sender,
                        token_id = params.token_id,
                        amount = sp.nat(1)
                    )
                ]
            )
        ])

        trans_nft = sp.contract(
            sp.TList(sp.TRecord(from_ = sp.TAddress, txs = sp.TList(sp.TRecord(amount = sp.TNat, to_ = sp.TAddress, token_id = sp.TNat).layout(("to_", ("token_id", "amount")))))),
            params.nft_con_addr,
            entry_point = 'transfer'
        ).open_some()

        sp.transfer(transfer_arg.value, sp.mutez(0), trans_nft)

        #assigning trade_val as zero
        self.data.trade_val = sp.nat(0)
        
        
        #sending amount to buyer from contract
        sp.send(params.seller_addr, self.data.nft_data[sp.record(user_addr = params.seller_addr, nft_con_data = params.nft_con_addr, token_id = params.token_id)].price)
        
        #updating is_for_sale
        self.data.nft_data[sp.record(user_addr = params.seller_addr, nft_con_data = params.nft_con_addr, token_id = params.token_id)].is_for_sale = sp.bool(False)
    
    @sp.entry_point
    def sell_nft(self, params):
        self.data.nft_data[sp.record(user_addr = sp.sender, nft_con_data = params.nft_con_addr, token_id = params.token_id)] = sp.record(price = params.price, is_for_sale = params.is_for_sale)
        pass

    @sp.entry_point
    def mint_nft(self, params):
        mint_con = sp.contract(
        sp.TRecord(
                address = sp.TAddress,
                token_id = sp.TNat,
                amount = sp.TNat,
                metadata = sp.TMap(sp.TString, sp.TBytes)
            ),
            params.token, 
            entry_point = 'mint'
        ).open_some()

        mint_data = sp.record(
            address = params.address,
            token_id = params.token_id,
            amount = params.amount,
            metadata = params.metadata
        )

        sp.transfer(mint_data, sp.mutez(0), mint_con)
        
#nft contract
FA2 = sp.io.import_script_from_url("https://smartpy.io/dev/templates/FA2.py")
class nft_contract(FA2.FA2):
    #minting NFT using owner NFT contract
   
    pass

@sp.add_test(name = 'tester')
def test():

    #test accounts start
    admin = sp.test_account("admin")
    userx = sp.test_account("userx")
    usery = sp.test_account("usery")
    userz = sp.test_account("userz")
    #test accounts end

    #scenario
    scenario = sp.test_scenario()

    #originating marketplace
    market_obj = marketplace_contract()
    scenario += market_obj
    
    #originating nft_contract
    # nft_obj = nft_contract(FA2.FA2_config(non_fungible = True), admin = admin.address, metadata= sp.big_map({"demo": sp.utils.bytes_of_string("tezos-storage:content"),"content": sp.utils.bytes_of_string("""{"name": "Tutorial Contract", "description": "NFT contract for the tutorial"}""")}))
    # scenario += nft_obj

    # nft_obj.mint(sp.record(address = userx.address, token_id = sp.nat(0), amount = sp.nat(1), metadata = sp.map({"userx": sp.utils.bytes_of_string("ipfs://bafkreih36m3d4yfbpyteluvntuph5xybwtgxdvyksbgyg66es44drk4hqy")}), token = nft_obj.address)).run(sender = admin.address)
    # nft_obj.mint(sp.record(address = usery.address, token_id = sp.nat(1), amount = sp.nat(1), metadata = sp.map({"usery": sp.utils.bytes_of_string("ipfs://bafkreih36m3d4yfbpyteluvntuph5xybwtgxdvyksbgyg66es44drk4hqy")}), token = nft_obj.address)).run(sender = admin.address)
    # nft_obj.mint(sp.record(address = userz.address, token_id = sp.nat(2), amount = sp.nat(1), metadata = sp.map({"userz": sp.utils.bytes_of_string("ipfs://bafkreih36m3d4yfbpyteluvntuph5xybwtgxdvyksbgyg66es44drk4hqy")}), token = nft_obj.address)).run(sender = admin.address)
    adminx = sp.address('tz1SLTUYZGNgYabBScpSqzmzNZNzczMAoEKA')
    administratorx = sp.address('KT1ScHD8Fp5qFxevWdJL8u1Hw6aYGAiWurVR')
    #minter
    nft_obj = nft_contract(FA2.FA2_config(non_fungible = True), admin = administratorx, metadata= sp.big_map({"demo": sp.utils.bytes_of_string("tezos-storage:content"),"content": sp.utils.bytes_of_string("""{"name": "Tutorial Contract", "description": "NFT contract for the tutorial"}""")}))
    scenario += nft_obj

    nft_obj.mint(sp.record(address = userx.address, token_id = sp.nat(0), amount = sp.nat(1), metadata = sp.map({"userz": sp.utils.bytes_of_string("ipfs://bafkreih36m3d4yfbpyteluvntuph5xybwtgxdvyksbgyg66es44drk4hqy")}), token = nft_obj.address)).run(sender = administratorx)
    nft_obj.mint(sp.record(address = usery.address, token_id = sp.nat(1), amount = sp.nat(1), metadata = sp.map({"userz": sp.utils.bytes_of_string("ipfs://bafkreih36m3d4yfbpyteluvntuph5xybwtgxdvyksbgyg66es44drk4hqy")}), token = nft_obj.address)).run(sender = administratorx)
    nft_obj.mint(sp.record(address = userz.address, token_id = sp.nat(2), amount = sp.nat(1), metadata = sp.map({"userz": sp.utils.bytes_of_string("ipfs://bafkreih36m3d4yfbpyteluvntuph5xybwtgxdvyksbgyg66es44drk4hqy")}), token = nft_obj.address)).run(sender = administratorx)

    #minter

    scenario += market_obj.add_partners(sp.record(dictkey = "self_nft_address", dictvalue = nft_obj.address)).run(sender = admin.address)
    scenario += market_obj.sell_nft(sp.record(nft_con_addr = nft_obj.address, token_id = sp.nat(0), price = sp.tez(900), is_for_sale = sp.bool(True))).run(sender = userx.address)
    scenario += market_obj.sell_nft(sp.record(nft_con_addr = nft_obj.address, token_id = sp.nat(1), price = sp.tez(10), is_for_sale = sp.bool(True))).run(sender = usery.address)
    scenario += market_obj.sell_nft(sp.record(nft_con_addr = nft_obj.address, token_id = sp.nat(2), price = sp.tez(1000), is_for_sale = sp.bool(True))).run(sender = userz.address)

    #updating operators starts here
    nft_obj.update_operators([
                sp.variant("add_operator", nft_obj.operator_param.make(
                    owner = userx.address,
                    operator = market_obj.address,
                    token_id = 0
                )),
            ]).run(sender = userx) 

    nft_obj.update_operators([
                sp.variant("add_operator", nft_obj.operator_param.make(
                    owner = usery.address,
                    operator = market_obj.address,
                    token_id = 1
                )),
            ]).run(sender = usery)

    nft_obj.update_operators([
                sp.variant("add_operator", nft_obj.operator_param.make(
                    owner = userz.address,
                    operator = market_obj.address,
                    token_id = 2
                )),
            ]).run(sender = userz)

    nft_obj.update_operators([
                sp.variant("add_operator", nft_obj.operator_param.make(
                    owner = usery.address,
                    operator = market_obj.address,
                    token_id = 2
                )),
            ]).run(sender = usery)   
    #updating operators ends here

    scenario += market_obj.buy_nft(sp.record(seller_addr = userx.address, nft_con_addr = nft_obj.address, token_id = sp.nat(0))).run(sender = usery.address, amount = sp.mutez(913500000))
    scenario += market_obj.sell_nft(sp.record(nft_con_addr = nft_obj.address, token_id = sp.nat(1), price = sp.tez(10), is_for_sale = sp.bool(True))).run(sender = usery.address)    
    scenario += market_obj.buy_nft(sp.record(seller_addr = usery.address, nft_con_addr = nft_obj.address, token_id = sp.nat(1))).run(sender = userx.address, amount = sp.mutez(10200000))  
    scenario += market_obj.buy_nft(sp.record(seller_addr = userz.address, nft_con_addr = nft_obj.address, token_id = sp.nat(2))).run(sender = usery.address, amount = sp.mutez(1015000000))
    scenario += market_obj.direct_transfer_nft(sp.record(reciever = userz.address, nft_con_addr = nft_obj.address, token_id = sp.nat(2))).run(sender = usery.address)
    
    scenario.show(market_obj.balance)
    scenario.show(userx.address)
    scenario.show(usery.address)
    scenario.show(userz.address)
    sp.add_compilation_target("nft_contract", nft_contract(FA2.FA2_config(non_fungible = True), admin = administratorx, metadata= sp.big_map({"demo": sp.utils.bytes_of_string("tezos-storage:content"),"content": sp.utils.bytes_of_string("""{"name": "Tutorial Contract", "description": "NFT contract for the tutorial"}""")})))
    sp.add_compilation_target("marketplace_contract", marketplace_contract())