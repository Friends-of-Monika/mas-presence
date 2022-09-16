
#
# Lightweight dependency-less Discord RPC implementation made solely for the
# needs of Discord Presence Submod for Monika After Story.
#
# Author: Herman S. <dreamscache.d@gmail.com>
#
# Sources:
# - https://github.com/ImKventis/MAS_RPC/blob/ab5209114d6165ad1c94a6d1aa75ccd695e3d1ef/game/Submods/Kventis_RPC/kventis_rpc.rpy
# - https://github.com/discord/discord-rpc/blob/master/documentation/hard-mode.md
# - https://discord.com/developers/docs/rich-presence/how-to
#

init -100 python in fom_presence:

    # Imports

    import platform
    import os
    import struct
    import json
    import io
    import uuid
    import errno
    import socket


    # Constants

    ## RPC opcodes

    OP_IDENTIFY = 0
    OP_DISPATCH = 1
    OP_CLOSE = 2
    OP_PING = 3
    OP_PONG = 4

    ## Command types

    CMD_SET_ACTIVITY = "SET_ACTIVITY"
    CMD_DISPATCH = "DISPATCH"

    ## Event types

    EVT_READY = "READY"
    EVT_ERROR = "ERROR"


    # Platform-specific approaches to IPC sockets (Unix) and pipes (Windows.)

    ## Unix domain socket

    class _UnixSocket(object):
        """
        Unix (Linux, Darwin) implementation of Discord RPC socket.

        Key differences from Windows implementation include "sendall" as "write"
        and "recv" as "read."
        """

        def __init__(self, socket):
            """
            Constructor function for creating a new socket abstraction wrapper
            from a Unix socket object (must support sendall, recv and close.)

            IN:
                socket -> socket:
                    Unix socket object to wrap.
            """

            self._sock = socket

        def write(self, data):
            """
            Writes the provided data array to this socket.

            IN:
                data -> Iterable[byte]:
                    Array, list or any other iterable containing bytes to write.
            """

            self._sock.sendall(data)

        def read(self, size):
            """
            Reads data into buffer of the specified size.

            IN:
                size -> int:
                    Amount of bytes to read from the socket.

            OUT:
                bytes:
                    Read buffer of data (size of 0 to size.)
            """

            return self._sock.recv(size)

        def close(self):
            """
            Closes the wrapped socket.
            """

            self._sock.close()

    def _unix_get_socket():
        """
        Locates Unix socket of Discord RPC using $XDG_RUNTIME_DIR, $TMPDIR,
        $TMP and $TEMP environment variables as base path and probes sockets
        0-9.

        OUT:
            socket.socket:
                Unix socket connected to Discord RPC socket.

            None:
                None is returned when Discord RPC socket could not be located.
        """

        # Find suitable runtime/temporary directory path from environment
        # variables, or fall back to /tmp. This below merely filters out all
        # None paths and picks the first, or returns "/tmp".
        base_path = ([path for path in map(os.environ.get, [
            "XDG_RUNTIME_DIR", "TMPDIR", "TMP", "TEMP"
        ]) if path is not None] or ["/tmp"])[0]

        # Now having base path, construct path to IPC socket. Try up to 10
        # possible paths (they all have suffix number.)
        for i in range(10):
            sock_path = os.path.join(base_path, "discord-ipc-{0}".format(i))

            if os.path.exists(sock_path):
                sock = socket.socket(socket.AF_UNIX)
                sock.connect(sock_path)
                return _UnixSocket(sock)

        return None

    ## Windows named pipe

    class _WindowsSocket(object):
        """
        Windows implementation of Discord RPC socket using named pipe.

        Key differences from Unix implementation include "write" as "sendall"
        and "read" as "recv."
        """

        def __init__(self, socket):
            """
            Constructor function for creating a new socket abstraction wrapper
            from a readable, writeable and closeable io object.

            IN:
                socket -> file:
                    File object to wrap.
            """

            self._sock = socket

        def write(self, data):
            """
            Writes the provided data array to this socket.

            IN:
                data -> Iterable[byte]:
                    Array, list or any other iterable containing bytes to write.
            """

            self._sock.write(data)

        def read(self, size):
            """
            Reads data into buffer of the specified size.

            IN:
                size -> int:
                    Amount of bytes to read from the socket.

            OUT:
                bytes:
                    Read buffer of data (size of 0 to size.)
            """

            return self._sock.read(size)

        def close(self):
            """
            Closes the wrapped socket.
            """

            self._sock.close()

    def _win_get_socket():
        """
        Uses Windows namespace path (\\?\pipe\ + pipe name) to open a named
        pipe that is a Discord RPC socket. Probes sockets 0-9.

        OUT:
            File object:
                File-like object connected to Discord RPC named pipe.

            None:
                None is returned when Discord RPC pipe could not be located.
        """

        # On Windows, using pipe namespace path like this.
        base_path = r"\\?\pipe"

        # Now having base path, construct path to IPC socket. Try up to 10
        # possible paths (they all have suffix number.)
        for i in range(10):
            sock_path = os.path.join(base_path, "discord-ipc-{0}".format(i))

            try:
                return _WindowsSocket(io.open(sock_path, "w+b"))

            except IOError as e:
                if e.errno != errno.EINVAL:
                    # Only raise if we're not trying to open closed or
                    # nonexistent pipe for reading and writing.
                    raise

        return None

    ## get_rpc_socket function definition

    if platform.system() == "Windows":
        get_rpc_socket = _win_get_socket
    else:
        get_rpc_socket = _unix_get_socket


    # User activity wrapper class definitions

    class Assets(object):
        """
        Assets class contains fields representing presence assets (large and
        small images) and their captions.
        """

        def __init__(
            self,
            large_image=None,
            large_text=None,
            small_image=None,
            small_text=None
        ):
            """
            Constructs a new Asset object with provided large/small images and
            their captions. Images may be asset names as well as image URLs.

            IN:
                large_image -> str, default None:
                    Large image asset key or URL.

                large_text -> str, default None:
                    Large image caption.

                small_image -> str, default None:
                    Small image asset key or URL.

                small_text -> str, default None:
                    Small image caption.
            """

            self.large_image = large_image
            self.large_text = large_text
            self.small_image = small_image
            self.small_text = small_text

        def to_dict(self):
            """
            Converts this object to dict.

            OUT:
                Dict[str, Any]:
                    Dictionary containing this object fields and their values.
            """

            d = dict()

            if self.large_image is not None:
                d["large_image"] = self.large_image
            if self.large_text is not None:
                d["large_text"] = self.large_text
            if self.small_image is not None:
                d["small_image"] = self.small_image
            if self.small_text is not None:
                d["small_text"] = self.small_text

            return d

    class Timestamps(object):
        """
        Timestamps class contaisn fields representing presence timestamps
        (start and end.)
        """

        def __init__(self, start=None, end=None):
            """
            Constructs a new Timestamps instance with provided timestamps.

            IN:
                start -> int, default None:
                    Start timestamp.

                end -> int, default None:
                    End timestamp.
            """

            self.start = start
            self.end = end

        def to_dict(self):
            """
            Converts this object to dict.

            OUT:
                Dict[str, Any]:
                    Dictionary containing this object fields and their values.
            """

            d = dict()

            if self.start is not None:
                d["start"] = self.start
            if self.end is not None:
                d["end"] = self.end

            return d

    class Activity(object):
        """
        Activity class represents Rich Presence activity.
        """

        def __init__(
            self,
            state=None,
            details=None,
            timestamps=None,
            assets=None
        ):
            """
            Constructs a new Activity instance with provided parameters.

            IN:
                state -> str or None, default None:
                    State of activity.

                details -> str or None, default None:
                    Details of activity.

                timestamps -> Timestamps or None, default None:
                    Timestamps of activity.

                assets -> Assets or None, default None:
                    Assets of activity.
            NOTE:
                See this chart to have an idea of what is what:
                https://discord.com/assets/43bef54c8aee2bc0fd1c717d5f8ae28a.png

                Not all parameters are supported, some were omitted as they
                did not fit the idea of the submod.
            """

            self.state = state
            self.details = details

            if timestamps is None:
                timestamps = Timestamps()
            self.timestamps = timestamps

            if assets is None:
                assets = Assets()
            self.assets = assets

        def to_dict(self):
            """
            Converts this object to dict recursively.

            OUT:
                Dict[str, Any]:
                    Dictionary containing this object fields and their values.
            """

            d = dict()

            if self.state is not None:
                d["state"] = self.state
            if self.details is not None:
                d["details"] = self.details

            d["timestamps"] = self.timestamps.to_dict()
            d["assets"] = self.assets.to_dict()

            return d


    # Packets and error responses implementation

    ## Packet implementation

    class Packet(object):
        def __init__(self, opcode, payload=None):
            self.opcode = opcode
            self.payload = payload

        @staticmethod
        def load(reader):
            # Read chunk of data for two 4-byte integers (opcode + length) and
            # unpack struct from it.
            # <II - less endian (<), opcode (I), packet length (I)
            op, dl = struct.unpack("<II", reader.read(8))

            # Read remaining data, decode as UTF-8 and parse JSON.
            dd = json.loads(reader.read(dl).decode("utf-8"))

            # Return packet with unpacked data.
            return Packet(op, dd)

        def dump(self, writer):
            # Serialize data as JSON and encode it as UTF-8 string.
            ds = json.dumps(self.payload, separators=(",", ":")).encode("utf-8")

            # Write two 4-byte integers (opcode + length) as packed struct
            # and write encoded data following it.
            # <II - less endian (<), opcode (I), packet length (I)
            buf = io.BytesIO()
            if self.payload is not None:
                buf.write(struct.pack("<II", self.opcode, len(ds)))
                buf.write(ds)
            else:
                buf.write(struct.pack("<II", self.opcode, 0))

            # Write buffer to writer.
            buf.seek(0)  # Reset to 0 after writing.
            writer.write(buf.read())

        def __str__(self):
            return "<Packet opcode={0} payload={1}>".format(self.opcode, self.payload)

    ## Packet type implementations as subclasses

    class Identify(Packet):
        def __init__(self, client_id):
            super(Identify, self).__init__(OP_IDENTIFY, dict(
                v=1, client_id=str(client_id)
            ))

    class Ping(Packet):
        def __init__(self):
            super(Ping, self).__init__(OP_PING, dict(msg="pong"))

    class Command(Packet):
        def __init__(self, command, args):
            super(Command, self).__init__(OP_DISPATCH, dict(
                cmd=command,
                args=args,
                nonce=str(uuid.uuid4())
            ))

    class SetActivity(Command):
        def __init__(self, activity):
            super(SetActivity, self).__init__(CMD_SET_ACTIVITY, dict(
                pid=os.getpid(),
                activity=activity.to_dict()
            ))


    ## Pre-initialized packets that can be reused without any changes.

    PACK_PING = Packet(OP_PING, dict(msg="pong"))

    ## Packet-wrapping error

    class CallError(Exception):
        def __init__(self, code, message):
            super(CallError, self).__init__(
                code, message
            )

            self.code = code
            self.message = message

        @staticmethod
        def from_packet(packet):
            if (
                packet.opcode == OP_CLOSE
                and "code" in packet.payload
                and "message" in packet.payload
            ):
                return CallError(packet.payload["code"], packet.payload["message"])

            elif (
                packet.payload.get("evt") == EVT_ERROR
                and "data" in packet.payload
            ):
                data = packet.payload["data"]
                return CallError(data["code"], data["message"])

            return None

        def __str__(self):
            return str("[Error {0}] {1}".format(self.code, self.message))


    # Remote Procedure Call client implementation

    class Client(object):
        def __init__(self, socket):
            self._sock = socket

        def call(self, packet):
            packet.dump(self._sock)
            rp = Packet.load(self._sock)

            err = CallError.from_packet(rp)
            if err is not None:
                raise err

            return rp

        def handshake(self, client_id):
            res_p = self.call(Identify(client_id))
            return res_p.payload["data"]

        def command(self, command, args):
            self.call(Command(command, args))

        def set_activity(self, activity):
            self.call(SetActivity(activity))

        def ping(self):
            self.call(Ping())

        def disconnect(self):
            self._sock.close()