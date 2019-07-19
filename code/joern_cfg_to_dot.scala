import scala.util.Try
import gremlin.scala._
import io.shiftleft.codepropertygraph.generated._
import java.nio.file.Paths
import io.shiftleft.queryprimitives.utils.ExpandTo
import org.apache.tinkerpop.gremlin.structure.Direction
import io.shiftleft.queryprimitives.steps.Implicits.JavaIteratorDeco
import javax.script.ScriptEngineManager
import scala.io.Source

/* APACHE from https://github.com/shiftleftsecurity/joern/ */
/* TODO: license properly */


/** Some helper functions: adapted from ReachingDefPass.scala in codeproperty graph repo */
def vertexToStr(vertex: Vertex, identifiers: Map[Vertex,Int]): String = {
  val str = new StringBuffer()

  str.append("id_")
  str.append(identifiers(vertex).toString)

  str.toString
}

def toDot(graph: ScalaGraph): String = {
  var vertex_identifiers:Map[Vertex,Int] = Map()

  var index = 0
  graph.V.l.foreach{ v =>
    vertex_identifiers += (v -> index)
    index += 1
  }

  val buf = new StringBuffer()

  buf.append("digraph g {\n")

  buf.append("# AST\n")
  buf.append("{\n")
  buf.append("  edge[color=green3,constraint=true]\n")
  graph.E.hasLabel("AST").l.foreach { e =>
    val parentVertex = vertexToStr(e.outVertex, vertex_identifiers).replace("\"","\'")
    val childVertex = vertexToStr(e.inVertex, vertex_identifiers).replace("\"","\'")
    buf.append(s"""  $parentVertex -> $childVertex \n """)
  }
  buf.append("}\n")

  buf.append("# CFG\n")
  buf.append("{\n")
  buf.append("edge[color=red3,constraint=false]\n")
  graph.E.hasLabel("CFG").l.foreach { e =>
    val parentVertex = vertexToStr(e.outVertex, vertex_identifiers).replace("\"","\'")
    val childVertex = vertexToStr(e.inVertex, vertex_identifiers).replace("\"","\'")
    buf.append(s"""  $parentVertex -> $childVertex \n """)
  }
  buf.append("}\n")

  buf.append("# REF\n")
  buf.append("{\n")
  buf.append("edge[color=purple3,constraint=false]\n")
  graph.E.hasLabel("REF").l.foreach { e =>
    val parentVertex = vertexToStr(e.outVertex, vertex_identifiers).replace("\"","\'")
    val childVertex = vertexToStr(e.inVertex, vertex_identifiers).replace("\"","\'")
    buf.append(s"""  $parentVertex -> $childVertex \n """)
  }
  buf.append("}\n")

  // buf.append("# EVAL_TYPE\n")
  // buf.append("{\n")
  // buf.append("edge[color=orangered1,constraint=true]\n")
  // graph.E.hasLabel("EVAL_TYPE").l.foreach { e =>
    // val parentVertex = vertexToStr(e.outVertex, vertex_identifiers).replace("\"","\'")
    // val childVertex = vertexToStr(e.inVertex, vertex_identifiers).replace("\"","\'")
  //   buf.append(s"""  $parentVertex -> $childVertex \n """)
  // }
  // buf.append("}\n")

  buf.append("# CALL\n")
  buf.append("{\n")
  buf.append("edge[color=blue1,constraint=false]\n")
  graph.E.hasLabel("CALL").l.foreach { e =>
    val parentVertex = vertexToStr(e.outVertex, vertex_identifiers).replace("\"","\'")
    val childVertex = vertexToStr(e.inVertex, vertex_identifiers).replace("\"","\'")
    buf.append(s"""  $parentVertex -> $childVertex \n """)
  }
  buf.append("}\n")

  buf.append("# VTABLE\n")
  buf.append("{\n")
  buf.append("edge[color=yellow2,constraint=false]\n")
  graph.E.hasLabel("VTABLE").l.foreach { e =>
    val parentVertex = vertexToStr(e.outVertex, vertex_identifiers).replace("\"","\'")
    val childVertex = vertexToStr(e.inVertex, vertex_identifiers).replace("\"","\'")
    buf.append(s"""  $parentVertex -> $childVertex \n """)
  }
  buf.append("}\n")

  buf.append("# INHERITS_FROM\n")
  buf.append("{\n")
  buf.append("edge[color=violetred2,constraint=false]\n")
  graph.E.hasLabel("INHERITS_FROM").l.foreach { e =>
    val parentVertex = vertexToStr(e.outVertex, vertex_identifiers).replace("\"","\'")
    val childVertex = vertexToStr(e.inVertex, vertex_identifiers).replace("\"","\'")
    buf.append(s"""  $parentVertex -> $childVertex \n """)
  }
  buf.append("}\n")

  buf.append("# BINDS_TO\n")
  buf.append("{\n")
  buf.append("edge[color=grey37,constraint=false]\n")
  graph.E.hasLabel("BINDS_TO").l.foreach { e =>
    val parentVertex = vertexToStr(e.outVertex, vertex_identifiers).replace("\"","\'")
    val childVertex = vertexToStr(e.inVertex, vertex_identifiers).replace("\"","\'")
    buf.append(s"""  $parentVertex -> $childVertex \n """)
  }
  buf.append("}\n")

  buf.append("}\n")

  buf.toString
}

toDot(cpg.graph)

/* read bug_names */
