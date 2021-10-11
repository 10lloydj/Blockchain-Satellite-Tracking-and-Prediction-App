const { expect } = require('chai')

//requests a usable contract abstraction for a solidity contract
const Satellites = artifacts.require('Satellites')

require('chai')
    .use(require('chai-as-promised'))
    .should()

contract('Satellites', (accounts) =>    {

    let satellite
    // Write tests here...
    before(async () => {
        // Load Contract
        satellite = await Satellites.new()
    })

    describe('Satellite Contract Development', async () => {
      it('has a name', async () => {
        const name = await satellite.name()
        assert.equal(name, 'Satellites Smart Contract')
      })
    })
    // satellite, no functions method, just set, doesnt return so check it does it or something
    describe('Satellite Contract Accessibility', async() => {
      it('set function saves data to the contract and get function returns an array of satellite data', async () => {
        // saves satellite data to the blockchain
        await satellite.set(0, 16, 'test', 'test', 'test', 'fggf', '2', '54')
        const satarray = await satellite.get()
        expect(satarray).to.be.a('object')
      })

      it('contract variables are retrievable by the get function', async() => {
        await satellite.set(0, 16, 'test', 'realtest', 'test1000', 'fggf', '2', '54')
        const satarray = await satellite.get()
        assert.equal(satarray[2], 'realtest')
      })
    })
    describe('Satellite Contract Amendment', async() => {
      it('set function updates the data in the contract', async() => {
        await satellite.set(0, 16, 'test', 'test', 'test', 'fggf', '2', '54')
        const satarray = await satellite.get()
        // didnt data
        await satellite.set(0, 16, 'test2', 'test2', 'test2', 'fggf22', '23', '5454')
        const satarray2 = await satellite.get()
        expect(satarray).to.not.equal(satarray2)
      })
    })
})