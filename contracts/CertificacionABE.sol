// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * CertificacionABE — ABE Academy NFT certificates (ERC-721)
 * Deployed on Polygon for low gas fees.
 * Non-transferable after emission (soulbound option per course).
 */
contract CertificacionABE is ERC721URIStorage, AccessControl {
    using Counters for Counters.Counter;

    bytes32 public constant EMISOR_ROLE = keccak256("EMISOR_ROLE");
    Counters.Counter private _tokenIds;

    struct Certificado {
        address alumno;
        string curso;
        uint256 fechaEmision;
        bool soulbound;
    }

    mapping(uint256 => Certificado) public certificados;
    mapping(address => uint256[]) public certificadosPorAlumno;

    event CertificadoEmitido(uint256 indexed tokenId, address indexed alumno, string curso);

    constructor() ERC721("Certificacion ABE", "CERTABE") {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(EMISOR_ROLE, msg.sender);
    }

    function emitirCertificado(
        address alumno,
        string memory metadataURI,
        string memory curso,
        bool soulbound
    ) external onlyRole(EMISOR_ROLE) returns (uint256) {
        _tokenIds.increment();
        uint256 newId = _tokenIds.current();

        _mint(alumno, newId);
        _setTokenURI(newId, metadataURI);

        certificados[newId] = Certificado({
            alumno: alumno,
            curso: curso,
            fechaEmision: block.timestamp,
            soulbound: soulbound
        });
        certificadosPorAlumno[alumno].push(newId);

        emit CertificadoEmitido(newId, alumno, curso);
        return newId;
    }

    function transferFrom(address from, address to, uint256 tokenId) public override(ERC721, IERC721) {
        require(!certificados[tokenId].soulbound, "Certificado soulbound: no transferible");
        super.transferFrom(from, to, tokenId);
    }

    function getCertificadosAlumno(address alumno) external view returns (uint256[] memory) {
        return certificadosPorAlumno[alumno];
    }

    function supportsInterface(bytes4 interfaceId) public view override(ERC721URIStorage, AccessControl) returns (bool) {
        return super.supportsInterface(interfaceId);
    }
}
